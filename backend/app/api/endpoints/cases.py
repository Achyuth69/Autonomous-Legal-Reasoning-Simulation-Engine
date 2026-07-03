from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.services.document_processor import DocumentProcessor
from app.services.orchestrator import LegalReasoningOrchestrator
from app.api.endpoints.sessions import get_session_config_sync, _db_load
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

cases_store: dict = {}


class CaseResponse(BaseModel):
    id: str
    title: str
    status: str
    created_at: str
    case_number: str


@router.post("/upload", response_model=CaseResponse)
async def upload_case_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "docx", "txt"]:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    # Resolve session config
    session_config = {}
    if session_id:
        session_config = get_session_config_sync(session_id)
        if not session_config:
            session_config = await _db_load(session_id)
        if not session_config:
            raise HTTPException(404, "Session not found. Please configure your API key on the setup page.")

    case_id     = str(uuid.uuid4())
    case_number = f"CASE-{datetime.now().strftime('%Y%m%d')}-{case_id[:8].upper()}"
    content     = await file.read()

    doc_processor = DocumentProcessor()
    file_path     = await doc_processor.save_upload(f"{case_id}_{file.filename}", content)
    extraction    = await doc_processor.extract_text(file_path, ext)

    if not extraction.get("text"):
        raise HTTPException(400, "Could not extract text from document")

    case_data = {
        "id": case_id, "case_number": case_number,
        "title": title or file.filename,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "document_path": file_path,
        "document_text": extraction["text"],
        "file_type": ext,
        "page_count": extraction.get("page_count", 0),
        "session_id": session_id or "",
        "provider": session_config.get("provider", ""),
        "model": session_config.get("model", ""),
    }
    cases_store[case_id] = case_data
    background_tasks.add_task(process_case_async, case_id, case_data, session_config)

    return CaseResponse(id=case_id, title=case_data["title"],
                        status="processing", created_at=case_data["created_at"],
                        case_number=case_number)


async def process_case_async(case_id: str, case_data: dict, session_config: dict):
    logger.info(f"Processing case {case_id} with provider={session_config.get('provider','fallback')}")
    try:
        orchestrator = LegalReasoningOrchestrator(session_config=session_config)
        results      = await orchestrator.process_case(case_data)
        cases_store[case_id].update({
            "status":                 results.get("status", "completed"),
            "facts":                  results.get("facts", []),
            "parties":                results.get("parties", {}),
            "timeline":               results.get("timeline", []),
            "jurisdiction":           results.get("jurisdiction", ""),
            "legal_issues":           results.get("legal_issues", []),
            "case_type":              results.get("case_type", ""),
            "statutes":               results.get("statutes", []),
            "precedents":             results.get("precedents", []),
            "plaintiff_arguments":    results.get("plaintiff_arguments", {}),
            "defendant_arguments":    results.get("defendant_arguments", {}),
            "judgment":               results.get("judgment", {}),
            "verdict":                results.get("verdict", ""),
            "confidence_score":       results.get("confidence_score", 0.0),
            "risk_analysis":          results.get("risk_analysis", {}),
            "plaintiff_strength":     results.get("plaintiff_strength", 0.0),
            "defendant_strength":     results.get("defendant_strength", 0.0),
            "citation_verification":  results.get("citation_verification", {}),
            "multi_model_debate":     results.get("multi_model_debate", {}),
            "ranked_evidence":        results.get("ranked_evidence", []),
            "constitutional_provisions": results.get("constitutional_provisions", []),
            "statutory_provisions":   results.get("statutory_provisions", []),
            "legal_principles":       results.get("legal_principles", []),
            "reasoning_chain":        results.get("reasoning_chain", []),
            "possible_outcomes":      results.get("possible_outcomes", []),
            "confidence_assessment":  results.get("confidence_assessment", {}),
            "structured_report":      results.get("structured_report", {}),
            "plaintiff_challenges":   results.get("plaintiff_challenges", []),
            "defendant_challenges":   results.get("defendant_challenges", []),
            "unknown_facts":          results.get("unknown_facts", []),
            "contradictions":         results.get("contradictions", []),
            "possible_violations":    results.get("possible_violations", []),
            "has_legal_kb":           results.get("has_legal_kb", False),
            "evidence_summary":       results.get("evidence_summary", ""),
            "agent_logs":             results.get("agent_logs", []),
            "completed_at":           datetime.utcnow().isoformat(),
        })
        logger.info(f"Case {case_id} completed")
    except Exception as e:
        logger.error(f"Case {case_id} failed: {e}")
        cases_store[case_id].update({"status": "failed", "error": str(e)})


@router.get("/{case_id}")
async def get_case(case_id: str):
    if case_id not in cases_store:
        raise HTTPException(404, "Case not found")
    return cases_store[case_id]


@router.get("/")
async def list_cases():
    return [
        {"id": k, "case_number": v["case_number"], "title": v["title"],
         "status": v["status"], "created_at": v["created_at"],
         "provider": v.get("provider",""), "model": v.get("model","")}
        for k, v in cases_store.items()
    ]


@router.delete("/{case_id}")
async def delete_case(case_id: str):
    if case_id not in cases_store:
        raise HTTPException(404, "Case not found")
    del cases_store[case_id]
    return {"message": "Deleted"}
