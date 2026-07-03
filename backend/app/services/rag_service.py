"""
RAG Service — Document-First Architecture
=========================================
Every legal conclusion must originate from uploaded documents.
Supports: Constitution, Law Books, Judgments, Notifications, Bare Acts.
Hybrid retrieval: Dense Embeddings + BM25 + Reranking.
"""
from __future__ import annotations
import os, json, hashlib, re
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy-loaded globals (initialised once per process)
_chroma_client: Optional[chromadb.ClientAPI] = None
_embed_model: Optional[SentenceTransformer] = None
_reranker: Optional[CrossEncoder] = None
_bm25_cache: Dict[str, BM25Okapi] = {}          # collection → BM25 index
_bm25_docs_cache: Dict[str, List[Dict]] = {}     # collection → raw chunks


def _get_chroma() -> chromadb.ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
        persist_dir.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB initialised", path=str(persist_dir))
    return _chroma_client


def _get_embed() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer loaded")
    return _embed_model


def _get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        try:
            _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("CrossEncoder reranker loaded")
        except Exception as e:
            logger.warning("Reranker unavailable", error=str(e))
    return _reranker


# ──────────────────────────────────────────────────────────────────────────────
# Chunking
# ──────────────────────────────────────────────────────────────────────────────

def _semantic_chunk(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Split text into overlapping chunks, respecting sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current, length = [], [], 0
    for sent in sentences:
        wc = len(sent.split())
        if length + wc > chunk_size and current:
            chunks.append(" ".join(current))
            # keep overlap
            keep, kept = [], 0
            for s in reversed(current):
                kept += len(s.split())
                keep.insert(0, s)
                if kept >= overlap:
                    break
            current, length = keep, kept
        current.append(sent)
        length += wc
    if current:
        chunks.append(" ".join(current))
    return chunks


def _extract_metadata(chunk: str, doc_name: str, chunk_idx: int) -> Dict[str, str]:
    """Extract Article/Section/Chapter references from chunk text."""
    meta: Dict[str, str] = {
        "document": doc_name,
        "chunk_index": str(chunk_idx),
    }
    for pattern, key in [
        (r"Article\s+(\d+[A-Z]?)", "article"),
        (r"Section\s+(\d+[A-Z]?)", "section"),
        (r"Chapter\s+([IVXLCDM]+|\d+)", "chapter"),
        (r"Clause\s+\(([a-z\d]+)\)", "clause"),
        (r"Schedule\s+([IVXLCDM]+|\d+)", "schedule"),
    ]:
        m = re.search(pattern, chunk, re.IGNORECASE)
        if m:
            meta[key] = m.group(1)
    # heading: first line if short
    first_line = chunk.split("\n")[0].strip()
    if len(first_line) < 120:
        meta["heading"] = first_line
    return meta


# ──────────────────────────────────────────────────────────────────────────────
# Ingestion
# ──────────────────────────────────────────────────────────────────────────────

class LegalRAGService:
    """Document-first RAG for the legal reasoning engine."""

    LEGAL_KB_COLLECTION = "legal_knowledge_base"
    CASE_COLLECTION_PREFIX = "case_"

    def __init__(self):
        self.chroma = _get_chroma()
        self.embed = _get_embed()

    def _collection(self, name: str) -> chromadb.Collection:
        return self.chroma.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    # ── ingest ─────────────────────────────────────────────────────────────

    def ingest_legal_document(
        self,
        text: str,
        doc_name: str,
        doc_type: str = "law",          # constitution | law | judgment | notification
        collection: str = LEGAL_KB_COLLECTION,
    ) -> int:
        """Chunk, embed and store a legal document. Returns number of chunks stored."""
        chunks = _semantic_chunk(text)
        if not chunks:
            return 0

        coll = self._collection(collection)
        embeddings = self.embed.encode(chunks, show_progress_bar=False).tolist()

        ids, docs, metas, embs = [], [], [], []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            chunk_id = hashlib.md5(f"{doc_name}:{i}:{chunk[:50]}".encode()).hexdigest()
            meta = _extract_metadata(chunk, doc_name, i)
            meta["doc_type"] = doc_type
            ids.append(chunk_id)
            docs.append(chunk)
            metas.append(meta)
            embs.append(emb)

        # upsert in batches of 100
        for start in range(0, len(ids), 100):
            coll.upsert(
                ids=ids[start:start + 100],
                documents=docs[start:start + 100],
                metadatas=metas[start:start + 100],
                embeddings=embs[start:start + 100],
            )

        # invalidate BM25 cache for this collection
        _bm25_cache.pop(collection, None)
        _bm25_docs_cache.pop(collection, None)

        logger.info("Ingested legal document", doc=doc_name, chunks=len(ids))
        return len(ids)

    def ingest_case_document(self, text: str, case_id: str, doc_name: str) -> int:
        """Index a case-specific uploaded document."""
        return self.ingest_legal_document(
            text, doc_name, "case_document",
            collection=f"{self.CASE_COLLECTION_PREFIX}{case_id}",
        )

    # ── BM25 helpers ───────────────────────────────────────────────────────

    def _get_bm25(self, collection: str):
        if collection not in _bm25_cache:
            coll = self._collection(collection)
            count = coll.count()
            if count == 0:
                return None, []
            results = coll.get(include=["documents", "metadatas"])
            docs_raw = [
                {"text": d, "meta": m}
                for d, m in zip(results["documents"], results["metadatas"])
            ]
            tokenised = [r["text"].lower().split() for r in docs_raw]
            _bm25_cache[collection] = BM25Okapi(tokenised)
            _bm25_docs_cache[collection] = docs_raw
        return _bm25_cache.get(collection), _bm25_docs_cache.get(collection, [])

    # ── retrieval ──────────────────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        collection: str = LEGAL_KB_COLLECTION,
        top_k: int = 10,
        doc_type_filter: Optional[str] = None,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval: Dense + BM25, then rerank.
        Returns list of evidence chunks with metadata.
        """
        coll = self._collection(collection)
        if coll.count() == 0:
            return []

        # ── dense retrieval ──
        q_emb = self.embed.encode([query], show_progress_bar=False).tolist()
        where = {"doc_type": doc_type_filter} if doc_type_filter else None
        dense_results = coll.query(
            query_embeddings=q_emb,
            n_results=min(top_k, coll.count()),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        dense_chunks = []
        for doc, meta, dist in zip(
            dense_results["documents"][0],
            dense_results["metadatas"][0],
            dense_results["distances"][0],
        ):
            dense_chunks.append({
                "text": doc,
                "meta": meta,
                "dense_score": float(1 - dist),   # cosine similarity
                "source": "dense",
            })

        # ── BM25 retrieval ──
        bm25, bm25_docs = self._get_bm25(collection)
        bm25_chunks = []
        if bm25 and bm25_docs:
            scores = bm25.get_scores(query.lower().split())
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            for idx in top_indices:
                if scores[idx] > 0:
                    item = bm25_docs[idx]
                    bm25_chunks.append({
                        "text": item["text"],
                        "meta": item["meta"],
                        "bm25_score": float(scores[idx]),
                        "source": "bm25",
                    })

        # ── merge + deduplicate ──
        seen, merged = set(), []
        for chunk in dense_chunks + bm25_chunks:
            key = chunk["text"][:100]
            if key not in seen:
                seen.add(key)
                merged.append(chunk)

        if not merged:
            return []

        # ── rerank ──
        if rerank:
            reranker = _get_reranker()
            if reranker:
                pairs = [(query, c["text"]) for c in merged]
                cross_scores = reranker.predict(pairs)
                for chunk, score in zip(merged, cross_scores):
                    chunk["rerank_score"] = float(score)
                merged.sort(key=lambda c: c.get("rerank_score", 0), reverse=True)
            else:
                # fallback: dense score
                merged.sort(key=lambda c: c.get("dense_score", 0), reverse=True)
        else:
            merged.sort(key=lambda c: c.get("dense_score", 0), reverse=True)

        # ── format output ──
        output = []
        for rank, chunk in enumerate(merged[:top_k], 1):
            meta = chunk["meta"]
            output.append({
                "rank": rank,
                "text": chunk["text"],
                "document": meta.get("document", "Unknown"),
                "doc_type": meta.get("doc_type", ""),
                "heading": meta.get("heading", ""),
                "article": meta.get("article", ""),
                "section": meta.get("section", ""),
                "chapter": meta.get("chapter", ""),
                "chunk_index": meta.get("chunk_index", ""),
                "similarity_score": round(chunk.get("dense_score", 0), 4),
                "rerank_score": round(chunk.get("rerank_score", 0), 4) if "rerank_score" in chunk else None,
                "confidence": _score_to_confidence(chunk.get("rerank_score") or chunk.get("dense_score", 0)),
                "retrieval_source": chunk["source"],
            })

        return output

    def retrieve_from_case(self, query: str, case_id: str, top_k: int = 8) -> List[Dict]:
        """Retrieve from case-specific uploaded documents."""
        return self.retrieve(query, f"{self.CASE_COLLECTION_PREFIX}{case_id}", top_k)

    def retrieve_constitution(self, query: str, top_k: int = 8) -> List[Dict]:
        return self.retrieve(query, self.LEGAL_KB_COLLECTION, top_k, doc_type_filter="constitution")

    def retrieve_law(self, query: str, top_k: int = 8) -> List[Dict]:
        return self.retrieve(query, self.LEGAL_KB_COLLECTION, top_k, doc_type_filter="law")

    def list_documents(self) -> List[Dict]:
        """List all ingested legal documents."""
        coll = self._collection(self.LEGAL_KB_COLLECTION)
        if coll.count() == 0:
            return []
        results = coll.get(include=["metadatas"])
        seen = {}
        for meta in results["metadatas"]:
            doc = meta.get("document", "Unknown")
            if doc not in seen:
                seen[doc] = {"name": doc, "type": meta.get("doc_type", ""), "chunks": 0}
            seen[doc]["chunks"] += 1
        return list(seen.values())

    def has_legal_kb(self) -> bool:
        """Check if any legal documents have been indexed."""
        try:
            coll = self._collection(self.LEGAL_KB_COLLECTION)
            return coll.count() > 0
        except Exception:
            return False


def _score_to_confidence(score: float) -> str:
    if score >= 0.8:
        return "HIGH"
    elif score >= 0.5:
        return "MEDIUM"
    elif score >= 0.2:
        return "LOW"
    return "VERY_LOW"


# Singleton
_rag_service: Optional[LegalRAGService] = None


def get_rag_service() -> LegalRAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = LegalRAGService()
    return _rag_service
