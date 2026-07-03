"""
LegalReasoningOrchestrator — 19-Agent Document-First Pipeline
=============================================================
Priority: Uploaded documents → LLM reasoning.
No agent invents facts, citations, or legal provisions.
"""
from __future__ import annotations
from typing import Dict, Any
import asyncio

# Existing agents (preserved)
from app.agents.case_intake_agent import CaseIntakeAgent
from app.agents.statute_research_agent import StatuteResearchAgent
from app.agents.caselaw_retrieval_agent import CaseLawRetrievalAgent
from app.agents.plaintiff_advocate_agent import PlaintiffAdvocateAgent
from app.agents.defendant_advocate_agent import DefendantAdvocateAgent
from app.agents.judge_agent import JudgeAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.citation_verification_agent import CitationVerificationAgent
from app.agents.multi_model_debate_agent import MultiModelDebateAgent

# New RAG-backed agents
from app.agents.rag_retrieval_agents import (
    FactExtractionAgent,
    LegalIssueIdentificationAgent,
    ConstitutionRetrievalAgent,
    LawBookRetrievalAgent,
    EvidenceRankingAgent,
    LegalPrincipleAgent,
    ReasoningAgent,
    CrossExaminationAgent,
    ConfidenceAssessmentAgent,
)
from app.agents.report_generation_agent import ReportGenerationAgent
from app.services.rag_service import get_rag_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class LegalReasoningOrchestrator:
    """
    19-agent orchestration pipeline.
    Steps 1-5: Document ingestion + fact/issue extraction
    Steps 6-7: RAG retrieval (Constitution + Law Books, parallel)
    Step  8:   Evidence ranking
    Step  9:   Legal principle derivation
    Step  10:  Reasoning chain
    Steps 11-12: Plaintiff + Defendant advocacy (parallel)
    Step  13:  Cross examination
    Steps 14-15: Judge + Risk analysis (parallel)
    Step  16:  Citation verification
    Step  17:  Multi-model debate (Groq)
    Step  18:  Confidence assessment
    Step  19:  Report generation
    """

    def __init__(self):
        # ── existing agents (unchanged) ──
        self.case_intake = CaseIntakeAgent()
        self.statute_research = StatuteResearchAgent()
        self.caselaw_retrieval = CaseLawRetrievalAgent()
        self.plaintiff_advocate = PlaintiffAdvocateAgent()
        self.defendant_advocate = DefendantAdvocateAgent()
        self.judge = JudgeAgent()
        self.risk_analysis = RiskAnalysisAgent()
        self.citation_verification = CitationVerificationAgent()
        self.multi_model_debate = MultiModelDebateAgent()
        # ── new agents ──
        self.fact_extraction = FactExtractionAgent()
        self.issue_identification = LegalIssueIdentificationAgent()
        self.constitution_retrieval = ConstitutionRetrievalAgent()
        self.law_book_retrieval = LawBookRetrievalAgent()
        self.evidence_ranking = EvidenceRankingAgent()
        self.legal_principle = LegalPrincipleAgent()
        self.reasoning = ReasoningAgent()
        self.cross_examination = CrossExaminationAgent()
        self.confidence_assessment = ConfidenceAssessmentAgent()
        self.report_generation = ReportGenerationAgent()
        self.rag = get_rag_service()

    # ──────────────────────────────────────────────────────────────────────
    async def process_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        results: Dict[str, Any] = {"agent_logs": []}
        doc_text = case_data.get("document_text", "")
        case_title = case_data.get("title", "Untitled Case")
        case_id = case_data.get("id", "")
        has_legal_kb = self.rag.has_legal_kb()

        logger.info("Starting 19-agent legal reasoning workflow",
                    has_kb=has_legal_kb, case_id=case_id)

        try:
            # ── STEP 1: Ingest case document into case-specific RAG ──
            logger.info("Step 1: Ingesting case document into RAG")
            if doc_text and case_id:
                chunks_stored = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.rag.ingest_case_document(doc_text, case_id, case_title)
                )
                logger.info(f"Ingested {chunks_stored} chunks for case {case_id}")

            # ── STEP 2: Case Intake (existing) ──
            logger.info("Step 2: Case Intake")
            intake_result = await self.case_intake.execute({
                "document_text": doc_text,
                "case_title": case_title
            })
            results["agent_logs"].append(intake_result)
            if intake_result["status"] != "success":
                raise Exception("Case intake failed")

            extracted = intake_result["result"]["extracted_data"]
            results["facts"] = (
                extracted.get("facts") or extracted.get("Facts") or []
            )
            results["parties"] = (
                extracted.get("parties") or extracted.get("Parties") or {}
            )
            results["timeline"] = (
                extracted.get("timeline") or extracted.get("Timeline") or []
            )
            results["jurisdiction"] = (
                extracted.get("jurisdiction") or extracted.get("Jurisdiction") or ""
            )
            results["legal_issues"] = (
                extracted.get("legal_issues") or extracted.get("Legal Issues") or []
            )
            results["case_type"] = (
                extracted.get("case_type") or extracted.get("Case Type") or ""
            )
            results["relief_sought"] = (
                extracted.get("relief_sought") or extracted.get("Relief Sought") or ""
            )

            # ── STEP 3: Fact Extraction (detailed) ──
            logger.info("Step 3: Fact Extraction")
            fact_result = await self.fact_extraction.execute({
                "document_text": doc_text,
                "case_title": case_title
            })
            results["agent_logs"].append(fact_result)
            if fact_result["status"] == "success":
                fe = fact_result["result"].get("extracted_facts", {})
                results["unknown_facts"] = fe.get("unknown_facts", [])
                results["contradictions"] = fe.get("contradictions", [])
                results["claims"] = fe.get("claims", [])
                if fe.get("established_facts"):
                    results["facts"] = fe["established_facts"]

            # ── STEP 4: Legal Issue Identification ──
            logger.info("Step 4: Legal Issue Identification")
            issue_result = await self.issue_identification.execute({
                "facts": results["facts"],
                "claims": results.get("claims", []),
                "case_type": results["case_type"],
            })
            results["agent_logs"].append(issue_result)
            if issue_result["status"] == "success":
                results["possible_violations"] = issue_result["result"].get("possible_violations", [])
                results["applicable_domains"] = issue_result["result"].get("applicable_domains", [])
                if issue_result["result"].get("primary_issues"):
                    results["legal_issues"] = (
                        issue_result["result"]["primary_issues"] +
                        issue_result["result"].get("secondary_issues", [])
                    )

            # ── STEP 5-6: RAG Retrieval (Constitution + Law, parallel) ──
            logger.info("Step 5-6: RAG Document Retrieval (parallel)")
            const_task = self.constitution_retrieval.execute({
                "legal_issues": results["legal_issues"],
                "facts": results["facts"],
            })
            law_task = self.law_book_retrieval.execute({
                "legal_issues": results["legal_issues"],
                "case_type": results["case_type"],
                "facts": results["facts"],
            })
            # Also run existing statute + caselaw research in parallel
            statute_task = self.statute_research.execute({
                "legal_issues": results["legal_issues"],
                "case_type": results["case_type"],
                "jurisdiction": results["jurisdiction"],
                "facts": results["facts"],
            })
            caselaw_task = self.caselaw_retrieval.execute({
                "legal_issues": results["legal_issues"],
                "case_type": results["case_type"],
                "jurisdiction": results["jurisdiction"],
                "facts": results["facts"],
            })

            const_result, law_result, statute_result, caselaw_result = await asyncio.gather(
                const_task, law_task, statute_task, caselaw_task
            )
            results["agent_logs"].extend([const_result, law_result, statute_result, caselaw_result])

            results["constitutional_provisions"] = (
                const_result["result"].get("constitutional_provisions", [])
                if const_result["status"] == "success" else []
            )
            results["statutory_provisions"] = (
                law_result["result"].get("statutory_provisions", [])
                if law_result["status"] == "success" else []
            )
            results["statutes"] = statute_result["result"].get("statutes", []) if statute_result["status"] == "success" else []
            results["precedents"] = caselaw_result["result"].get("precedents", []) if caselaw_result["status"] == "success" else []

            # Retrieve case-doc chunks for evidence ranking
            case_chunks = []
            if case_id:
                for issue in results["legal_issues"][:3]:
                    case_chunks.extend(
                        await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda q=issue: self.rag.retrieve_from_case(q, case_id, top_k=4)
                        )
                    )

            # ── STEP 7: Evidence Ranking ──
            logger.info("Step 7: Evidence Ranking")
            evidence_result = await self.evidence_ranking.execute({
                "constitutional_provisions": results["constitutional_provisions"],
                "statutory_provisions": results["statutory_provisions"],
                "case_document_chunks": case_chunks,
                "legal_issues": results["legal_issues"],
            })
            results["agent_logs"].append(evidence_result)
            results["ranked_evidence"] = (
                evidence_result["result"].get("ranked_evidence", [])
                if evidence_result["status"] == "success" else []
            )
            results["evidence_summary"] = (
                evidence_result["result"].get("evidence_summary", "")
                if evidence_result["status"] == "success" else ""
            )

            # ── STEP 8: Legal Principles ──
            logger.info("Step 8: Legal Principle Derivation")
            principle_result = await self.legal_principle.execute({
                "ranked_evidence": results["ranked_evidence"],
                "legal_issues": results["legal_issues"],
                "case_type": results["case_type"],
            })
            results["agent_logs"].append(principle_result)
            results["legal_principles"] = (
                principle_result["result"].get("legal_principles", [])
                if principle_result["status"] == "success" else []
            )

            # ── STEP 9: Reasoning Chain ──
            logger.info("Step 9: Reasoning Chain")
            reasoning_result = await self.reasoning.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "ranked_evidence": results["ranked_evidence"],
                "legal_principles": results["legal_principles"],
                "parties": results["parties"],
            })
            results["agent_logs"].append(reasoning_result)
            results["reasoning_chain"] = (
                reasoning_result["result"].get("reasoning_chain", [])
                if reasoning_result["status"] == "success" else []
            )
            results["possible_outcomes"] = (
                reasoning_result["result"].get("possible_outcomes", [])
                if reasoning_result["status"] == "success" else []
            )

            # ── STEP 10-11: Plaintiff + Defendant (parallel) ──
            logger.info("Step 10-11: Advocacy (parallel)")
            plaintiff_task = self.plaintiff_advocate.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "parties": results["parties"],
                "relief_sought": results["relief_sought"],
                "ranked_evidence": results["ranked_evidence"],
                "legal_principles": results["legal_principles"],
            })
            defendant_task = self.defendant_advocate.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "parties": results["parties"],
                "plaintiff_arguments": {},
                "ranked_evidence": results["ranked_evidence"],
            })
            plaintiff_result, defendant_result = await asyncio.gather(
                plaintiff_task, defendant_task
            )
            results["agent_logs"].extend([plaintiff_result, defendant_result])
            results["plaintiff_arguments"] = (
                plaintiff_result["result"].get("plaintiff_arguments", {})
                if plaintiff_result["status"] == "success" else {}
            )
            results["defendant_arguments"] = (
                defendant_result["result"].get("defendant_arguments", {})
                if defendant_result["status"] == "success" else {}
            )

            # ── STEP 12: Cross Examination ──
            logger.info("Step 12: Cross Examination")
            cross_result = await self.cross_examination.execute({
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "ranked_evidence": results["ranked_evidence"],
            })
            results["agent_logs"].append(cross_result)
            results["plaintiff_challenges"] = (
                cross_result["result"].get("plaintiff_challenges", [])
                if cross_result["status"] == "success" else []
            )
            results["defendant_challenges"] = (
                cross_result["result"].get("defendant_challenges", [])
                if cross_result["status"] == "success" else []
            )

            # ── STEP 13: Judge ──
            logger.info("Step 13: Judge")
            judge_result = await self.judge.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "parties": results["parties"],
                "ranked_evidence": results["ranked_evidence"],
                "reasoning_chain": results["reasoning_chain"],
            })
            results["agent_logs"].append(judge_result)
            results["judgment"] = judge_result["result"].get("judgment", {}) if judge_result["status"] == "success" else {}
            results["verdict"] = judge_result["result"].get("verdict", "") if judge_result["status"] == "success" else ""
            results["confidence_score"] = judge_result["result"].get("confidence_score", 0.0) if judge_result["status"] == "success" else 0.0

            # ── STEP 14-15: Risk + Citation (parallel) ──
            logger.info("Step 14-15: Risk + Citation (parallel)")
            risk_task = self.risk_analysis.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "judgment": results["judgment"],
            })
            citation_task = self.citation_verification.execute({
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
            })
            risk_result, citation_result = await asyncio.gather(risk_task, citation_task)
            results["agent_logs"].extend([risk_result, citation_result])
            results["risk_analysis"] = risk_result["result"].get("risk_analysis", {}) if risk_result["status"] == "success" else {}
            results["plaintiff_strength"] = risk_result["result"].get("plaintiff_strength", 0.0) if risk_result["status"] == "success" else 0.0
            results["defendant_strength"] = risk_result["result"].get("defendant_strength", 0.0) if risk_result["status"] == "success" else 0.0
            results["citation_verification"] = citation_result["result"].get("verification_results", {}) if citation_result["status"] == "success" else {}

            # ── STEP 16: Multi-Model Debate ──
            logger.info("Step 16: Multi-Model Debate")
            debate_result = await self.multi_model_debate.execute({
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "statutes": results["statutes"],
                "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "judgment": results["judgment"],
                "parties": results["parties"],
                "ranked_evidence": results["ranked_evidence"],
            })
            results["agent_logs"].append(debate_result)
            if debate_result["status"] == "success":
                results["multi_model_debate"] = {
                    "debate_transcript": debate_result.get("debate_transcript", []),
                    "final_consensus": debate_result.get("final_consensus", ""),
                    "participating_models": debate_result["result"].get("participating_models", []),
                    "total_rounds": debate_result["result"].get("total_rounds", 0),
                }
            else:
                results["multi_model_debate"] = {
                    "status": debate_result.get("status", "skipped"),
                    "error": debate_result.get("error", ""),
                }

            # ── STEP 17: Confidence Assessment ──
            logger.info("Step 17: Confidence Assessment")
            conf_result = await self.confidence_assessment.execute({
                "ranked_evidence": results["ranked_evidence"],
                "reasoning_chain": results["reasoning_chain"],
                "judgment": results["judgment"],
                "citation_verification": results["citation_verification"],
                "has_legal_kb": has_legal_kb,
            })
            results["agent_logs"].append(conf_result)
            results["confidence_assessment"] = (
                conf_result["result"] if conf_result["status"] == "success" else {}
            )

            # ── STEP 18: Report Generation ──
            logger.info("Step 18: Report Generation")
            report_result = await self.report_generation.execute({
                "case_title": case_title,
                "parties": results["parties"],
                "facts": results["facts"],
                "legal_issues": results["legal_issues"],
                "timeline": results["timeline"],
                "ranked_evidence": results["ranked_evidence"],
                "legal_principles": results["legal_principles"],
                "constitutional_provisions": results["constitutional_provisions"],
                "statutory_provisions": results["statutory_provisions"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "plaintiff_challenges": results["plaintiff_challenges"],
                "defendant_challenges": results["defendant_challenges"],
                "reasoning_chain": results["reasoning_chain"],
                "judgment": results["judgment"],
                "risk_analysis": results["risk_analysis"],
                "multi_model_debate": results["multi_model_debate"],
                "confidence_assessment": results["confidence_assessment"],
                "evidence_summary": results["evidence_summary"],
                "unknown_facts": results.get("unknown_facts", []),
                "contradictions": results.get("contradictions", []),
                "possible_violations": results.get("possible_violations", []),
                "case_type": results["case_type"],
                "jurisdiction": results["jurisdiction"],
            })
            results["agent_logs"].append(report_result)
            results["structured_report"] = (
                report_result["result"].get("report", {})
                if report_result["status"] == "success" else {}
            )

            results["has_legal_kb"] = has_legal_kb
            results["status"] = "completed"
            logger.info("19-agent workflow completed", case_id=case_id)

        except Exception as e:
            logger.error(f"Workflow error: {str(e)}", case_id=case_id)
            results["status"] = "failed"
            results["error"] = str(e)

        return results
