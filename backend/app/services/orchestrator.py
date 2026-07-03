from typing import Dict, Any, List
import asyncio
from app.agents.case_intake_agent import CaseIntakeAgent
from app.agents.statute_research_agent import StatuteResearchAgent
from app.agents.caselaw_retrieval_agent import CaseLawRetrievalAgent
from app.agents.plaintiff_advocate_agent import PlaintiffAdvocateAgent
from app.agents.defendant_advocate_agent import DefendantAdvocateAgent
from app.agents.judge_agent import JudgeAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.citation_verification_agent import CitationVerificationAgent
from app.agents.multi_model_debate_agent import MultiModelDebateAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class LegalReasoningOrchestrator:
    """Orchestrates the multi-agent legal reasoning workflow"""
    
    def __init__(self):
        self.case_intake = CaseIntakeAgent()
        self.statute_research = StatuteResearchAgent()
        self.caselaw_retrieval = CaseLawRetrievalAgent()
        self.plaintiff_advocate = PlaintiffAdvocateAgent()
        self.defendant_advocate = DefendantAdvocateAgent()
        self.judge = JudgeAgent()
        self.risk_analysis = RiskAnalysisAgent()
        self.citation_verification = CitationVerificationAgent()
        self.multi_model_debate = MultiModelDebateAgent()
    
    async def process_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a legal case through the complete multi-agent workflow
        
        Workflow:
        1. Case Intake - Extract facts and issues
        2. Statute Research - Find applicable law
        3. Case Law Retrieval - Find precedents
        4. Plaintiff Advocate - Build plaintiff's case
        5. Defendant Advocate - Build defense
        6. Judge - Render judgment
        7. Risk Analysis - Assess litigation risks
        8. Citation Verification - Validate citations
        """
        logger.info("Starting legal reasoning workflow")
        results = {"agent_logs": []}
        
        try:
            # Step 1: Case Intake
            logger.info("Step 1: Case Intake")
            intake_result = await self.case_intake.execute({
                "document_text": case_data.get("document_text", ""),
                "case_title": case_data.get("title", "Untitled Case")
            })
            results["agent_logs"].append(intake_result)
            
            if intake_result["status"] != "success":
                raise Exception("Case intake failed")
            
            extracted = intake_result["result"]["extracted_data"]
            results["facts"] = extracted.get("facts", [])
            results["parties"] = extracted.get("parties", {})
            results["timeline"] = extracted.get("timeline", [])
            results["jurisdiction"] = extracted.get("jurisdiction", "")
            results["legal_issues"] = extracted.get("legal_issues", [])
            results["case_type"] = extracted.get("case_type", "")
            results["relief_sought"] = extracted.get("relief_sought", "")
            
            # Step 2 & 3: Research Law and Precedents (in parallel)
            logger.info("Step 2 & 3: Legal Research (parallel)")
            
            statute_task = self.statute_research.execute({
                "legal_issues": results["legal_issues"],
                "case_type": results["case_type"],
                "jurisdiction": results["jurisdiction"],
                "facts": results["facts"]
            })
            
            caselaw_task = self.caselaw_retrieval.execute({
                "legal_issues": results["legal_issues"],
                "case_type": results["case_type"],
                "jurisdiction": results["jurisdiction"],
                "facts": results["facts"]
            })
            
            statute_result, caselaw_result = await asyncio.gather(
                statute_task, caselaw_task
            )
            
            results["agent_logs"].extend([statute_result, caselaw_result])
            
            results["statutes"] = statute_result["result"].get("statutes", [])
            results["precedents"] = caselaw_result["result"].get("precedents", [])
            
            # Step 4: Plaintiff Advocate
            logger.info("Step 4: Plaintiff Arguments")
            plaintiff_result = await self.plaintiff_advocate.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "parties": results["parties"],
                "relief_sought": results["relief_sought"]
            })
            results["agent_logs"].append(plaintiff_result)
            results["plaintiff_arguments"] = plaintiff_result["result"].get("plaintiff_arguments", {})
            
            # Step 5: Defendant Advocate
            logger.info("Step 5: Defendant Arguments")
            defendant_result = await self.defendant_advocate.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "parties": results["parties"],
                "plaintiff_arguments": results["plaintiff_arguments"]
            })
            results["agent_logs"].append(defendant_result)
            results["defendant_arguments"] = defendant_result["result"].get("defendant_arguments", {})
            
            # Step 6: Judge
            logger.info("Step 6: Judicial Decision")
            judge_result = await self.judge.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "parties": results["parties"]
            })
            results["agent_logs"].append(judge_result)
            results["judgment"] = judge_result["result"].get("judgment", {})
            results["verdict"] = judge_result["result"].get("verdict", "")
            results["confidence_score"] = judge_result["result"].get("confidence_score", 0.0)
            
            # Step 7 & 8: Risk Analysis and Citation Verification (in parallel)
            logger.info("Step 7 & 8: Risk Analysis and Citation Verification (parallel)")
            
            risk_task = self.risk_analysis.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "judgment": results["judgment"]
            })
            
            citation_task = self.citation_verification.execute({
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"]
            })
            
            risk_result, citation_result = await asyncio.gather(
                risk_task, citation_task
            )
            
            results["agent_logs"].extend([risk_result, citation_result])
            
            results["risk_analysis"] = risk_result["result"].get("risk_analysis", {})
            results["plaintiff_strength"] = risk_result["result"].get("plaintiff_strength", 0.0)
            results["defendant_strength"] = risk_result["result"].get("defendant_strength", 0.0)
            results["citation_verification"] = citation_result["result"].get("verification_results", {})
            
            # Step 9: Multi-Model Debate (Optional - if Groq is configured)
            logger.info("Step 9: Multi-Model Debate")
            debate_result = await self.multi_model_debate.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "judgment": results["judgment"],
                "parties": results["parties"]
            })
            results["agent_logs"].append(debate_result)
            
            if debate_result["status"] == "success":
                results["multi_model_debate"] = {
                    "debate_transcript": debate_result.get("debate_transcript", []),
                    "final_consensus": debate_result.get("final_consensus", ""),
                    "participating_models": debate_result["result"].get("participating_models", []),
                    "total_rounds": debate_result["result"].get("total_rounds", 0)
                }
            else:
                results["multi_model_debate"] = {
                    "status": debate_result.get("status", "skipped"),
                    "error": debate_result.get("error", "Debate not available")
                }
            
            logger.info("Legal reasoning workflow completed successfully")
            results["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
