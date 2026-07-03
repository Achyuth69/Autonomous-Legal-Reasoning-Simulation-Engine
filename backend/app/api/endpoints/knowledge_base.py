"""
Knowledge Base API — upload and manage legal documents (Constitution, Law Books, Judgments).
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import asyncio

from app.services.document_processor import DocumentProcessor
from app.services.rag_service import get_rag_service
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

DOC_TYPES = ["constitution", "law", "judgment", "notification", "bare_act", "circular"]


@router.post("/upload")
async def upload_legal_document(
    file: UploadFile = File(...),
    doc_type: str = Form("law"),
    doc_name: Optional[str] = Form(None),
):
    """Upload a legal document to the knowledge base (Constitution, Law Books, Judgments, etc.)"""
    if doc_type not in DOC_TYPES:
        raise HTTPException(400, f"doc_type must be one of: {', '.join(DOC_TYPES)}")

    allowed = ["pdf", "docx", "txt"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    content = await file.read()
    processor = DocumentProcessor()
    file_path = await processor.save_upload(f"kb_{file.filename}", content)
    extraction = await processor.extract_text(file_path, ext)

    text = extraction.get("text", "")
    if not text:
        raise HTTPException(400, "Could not extract text from document")

    name = doc_name or file.filename
    rag = get_rag_service()

    chunks = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: rag.ingest_legal_document(text, name, doc_type)
    )

    logger.info("Legal document indexed", name=name, type=doc_type, chunks=chunks)
    return {
        "success": True,
        "document_name": name,
        "doc_type": doc_type,
        "chunks_indexed": chunks,
        "message": f"Successfully indexed '{name}' ({chunks} chunks)"
    }


@router.get("/documents")
async def list_documents():
    """List all documents in the legal knowledge base."""
    rag = get_rag_service()
    docs = rag.list_documents()
    return {
        "documents": docs,
        "total": len(docs),
        "has_knowledge_base": len(docs) > 0
    }


@router.get("/status")
async def kb_status():
    """Check knowledge base status."""
    rag = get_rag_service()
    docs = rag.list_documents()
    has_constitution = any(d["type"] == "constitution" for d in docs)
    has_laws = any(d["type"] in ["law", "bare_act"] for d in docs)
    return {
        "total_documents": len(docs),
        "has_constitution": has_constitution,
        "has_laws": has_laws,
        "ready": len(docs) > 0,
        "documents": docs,
    }


@router.post("/search")
async def search_knowledge_base(query: str, doc_type: Optional[str] = None, top_k: int = 5):
    """Search the legal knowledge base."""
    rag = get_rag_service()
    if not rag.has_legal_kb():
        return {"results": [], "message": "No documents in knowledge base"}
    results = rag.retrieve(query, top_k=top_k, doc_type_filter=doc_type)
    return {"results": results, "total": len(results)}
