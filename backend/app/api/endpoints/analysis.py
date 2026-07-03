from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.agents.case_intake_agent import CaseIntakeAgent
from app.agents.statute_research_agent import StatuteResearchAgent

router = APIRouter()


class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str  # "extract", "statute_research", etc.


@router.post("/text")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze raw text using specific agent"""
    
    if request.analysis_type == "extract":
        agent = CaseIntakeAgent()
        result = await agent.execute({
            "document_text": request.text,
            "case_title": "Text Analysis"
        })
        return result
    
    elif request.analysis_type == "statute":
        # Requires legal issues to be provided
        raise HTTPException(
            status_code=400,
            detail="Statute research requires legal issues to be specified"
        )
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown analysis type: {request.analysis_type}"
        )


@router.get("/statistics")
async def get_statistics():
    """Get system statistics"""
    # In production, this would query the database
    return {
        "total_cases": 0,
        "completed_cases": 0,
        "pending_cases": 0,
        "success_rate": 0.0,
        "average_processing_time": 0.0
    }
