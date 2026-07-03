from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid
from app.services.document_processor import DocumentProcessor
from app.services.orchestrator import LegalReasoningOrchestrator
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# In-memory storage for demo (replace with database in production)
cases_store = {}


class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    case_type: Optional[str] = None


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
    title: Optional[str] = None
):
    """Upload a legal document and start case analysis"""
    
    # Validate file
    allowed_extensions = ["pdf", "docx", "txt"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate case ID
    case_id = str(uuid.uuid4())
    case_number = f"CASE-{datetime.now().strftime('%Y%m%d')}-{case_id[:8].upper()}"
    
    # Read file content
    content = await file.read()
    
    # Process document
    doc_processor = DocumentProcessor()
    file_path = await doc_processor.save_upload(f"{case_id}_{file.filename}", content)
    
    # Extract text
    extraction_result = await doc_processor.extract_text(file_path, file_ext)
    
    if not extraction_result.get("text"):
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from document"
        )
    
    # Create case record
    case_data = {
        "id": case_id,
        "case_number": case_number,
        "title": title or file.filename,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "document_path": file_path,
        "document_text": extraction_result["text"],
        "file_type": file_ext,
        "page_count": extraction_result.get("page_count", 0)
    }
    
    cases_store[case_id] = case_data
    
    # Start background processing
    background_tasks.add_task(process_case_async, case_id, case_data)
    
    return CaseResponse(
        id=case_id,
        title=case_data["title"],
        status=case_data["status"],
        created_at=case_data["created_at"],
        case_number=case_number
    )


async def process_case_async(case_id: str, case_data: dict):
    """Background task to process case through AI agents"""
    logger.info(f"Starting case processing: {case_id}")
    
    try:
        orchestrator = LegalReasoningOrchestrator()
        results = await orchestrator.process_case(case_data)
        
        # Update case with results
        cases_store[case_id].update({
            "status": results.get("status", "completed"),
            "facts": results.get("facts", []),
            "parties": results.get("parties", {}),
            "timeline": results.get("timeline", []),
            "jurisdiction": results.get("jurisdiction", ""),
            "legal_issues": results.get("legal_issues", []),
            "case_type": results.get("case_type", ""),
            "statutes": results.get("statutes", []),
            "precedents": results.get("precedents", []),
            "plaintiff_arguments": results.get("plaintiff_arguments", {}),
            "defendant_arguments": results.get("defendant_arguments", {}),
            "judgment": results.get("judgment", {}),
            "verdict": results.get("verdict", ""),
            "confidence_score": results.get("confidence_score", 0.0),
            "risk_analysis": results.get("risk_analysis", {}),
            "plaintiff_strength": results.get("plaintiff_strength", 0.0),
            "defendant_strength": results.get("defendant_strength", 0.0),
            "citation_verification": results.get("citation_verification", {}),
            "agent_logs": results.get("agent_logs", []),
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Case processing completed: {case_id}")
        
    except Exception as e:
        logger.error(f"Error processing case {case_id}: {str(e)}")
        cases_store[case_id].update({
            "status": "failed",
            "error": str(e)
        })


@router.get("/{case_id}")
async def get_case(case_id: str):
    """Get case details and analysis results"""
    if case_id not in cases_store:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return cases_store[case_id]


@router.get("/")
async def list_cases():
    """List all cases"""
    return [
        {
            "id": case_id,
            "case_number": case["case_number"],
            "title": case["title"],
            "status": case["status"],
            "created_at": case["created_at"]
        }
        for case_id, case in cases_store.items()
    ]


@router.delete("/{case_id}")
async def delete_case(case_id: str):
    """Delete a case"""
    if case_id not in cases_store:
        raise HTTPException(status_code=404, detail="Case not found")
    
    del cases_store[case_id]
    return {"message": "Case deleted successfully"}
