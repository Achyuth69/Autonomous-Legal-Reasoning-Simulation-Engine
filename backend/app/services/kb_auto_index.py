"""
Auto-index pre-uploaded legal documents from Knowledge_base/ folder on startup.
Runs once per process. Skips if documents are already indexed.
"""
from __future__ import annotations
import os
from pathlib import Path
from app.core.logging import get_logger

logger = get_logger(__name__)

# Map filename patterns → doc_type
FILENAME_TYPE_MAP = {
    "constitution": "constitution",
    "law_of_india": "law",
    "the_law_of_india": "law",
    "ipc": "law",
    "crpc": "law",
    "bnss": "law",
    "bns": "law",
    "bsa": "law",
    "evidence_act": "law",
    "judgment": "judgment",
    "notification": "notification",
    "circular": "notification",
    "bare_act": "bare_act",
}


def _detect_type(filename: str) -> str:
    lower = filename.lower().replace(" ", "_").replace("-", "_")
    for keyword, doc_type in FILENAME_TYPE_MAP.items():
        if keyword in lower:
            return doc_type
    return "law"


async def auto_index_knowledge_base():
    """
    Called once at startup. Indexes all PDFs in Knowledge_base/ folder
    if they are not already in ChromaDB.
    """
    kb_dir = Path("../Knowledge_base")
    if not kb_dir.exists():
        kb_dir = Path("Knowledge_base")
    if not kb_dir.exists():
        logger.info("No Knowledge_base folder found — skipping auto-index")
        return

    pdf_files = list(kb_dir.glob("*.pdf")) + list(kb_dir.glob("*.txt")) + list(kb_dir.glob("*.docx"))
    if not pdf_files:
        logger.info("Knowledge_base folder is empty — skipping auto-index")
        return

    from app.services.rag_service import get_rag_service
    from app.services.document_processor import DocumentProcessor

    rag = get_rag_service()
    already_indexed = {d["name"] for d in rag.list_documents()}

    processor = DocumentProcessor()
    indexed_count = 0

    for file_path in pdf_files:
        doc_name = file_path.name
        if doc_name in already_indexed:
            logger.info(f"Already indexed, skipping: {doc_name}")
            continue

        logger.info(f"Auto-indexing: {doc_name}")
        try:
            ext = file_path.suffix.lstrip(".").lower()
            extraction = await processor.extract_text(str(file_path), ext)
            text = extraction.get("text", "")
            if not text:
                logger.warning(f"No text extracted from {doc_name}")
                continue

            doc_type = _detect_type(doc_name)
            chunks = rag.ingest_legal_document(text, doc_name, doc_type)
            logger.info(f"Indexed {doc_name} as '{doc_type}' — {chunks} chunks")
            indexed_count += 1
        except Exception as e:
            logger.error(f"Failed to index {doc_name}: {e}")

    if indexed_count:
        logger.info(f"Auto-indexed {indexed_count} legal documents into Knowledge Base")
    else:
        logger.info("All Knowledge_base documents already indexed")
