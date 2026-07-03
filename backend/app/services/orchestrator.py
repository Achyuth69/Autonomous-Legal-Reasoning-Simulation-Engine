"""
LegalReasoningOrchestrator — 19-Agent Document-First Pipeline
Session config (provider/api_key/model) passed to every agent.
"""
from __future__ import annotations
from typing import Dict, Any, Optional
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
from app.agents.rag_retrieval_agents import (
    FactExtractionAgent, LegalIssueIdentificationAgent,
    ConstitutionRetrievalAgent, LawBookRetrievalAgent,
    EvidenceRankingAgent, LegalPrincipleAgent,
    ReasoningAgent, CrossExaminationAgent, ConfidenceAssessmentAgent,
)
from app.agents.report_generation_agent import ReportGenerationAgent
from app.services.rag_service import get_rag_service
from app.core.logging import get_logger

logger = get_logger(__name__)


def _make(cls, session_config):
    """Instantiate agent with session_config if constructor accepts it."""
    try:
        return cls(session_config=session_config)
    except TypeError:
        return cls()


class LegalReasoningOrchestrator:
    def __init__(self, session_config: Optional[Dict] = None):
        sc = session_config or {}
        self.session_config = sc
        self.case_intake           = _make(CaseIntakeAgent, sc)
        self.statute_research      = _make(StatuteResearchAgent, sc)
        self.caselaw_retrieval     = _make(CaseLawRetrievalAgent, sc)
        self.plaintiff_advocate    = _make(PlaintiffAdvocateAgent, sc)
        self.defendant_advocate    = _make(DefendantAdvocateAgent, sc)
        self.judge                 = _make(JudgeAgent, sc)
        self.risk_analysis         = _make(RiskAnalysisAgent, sc)
        self.citation_verification = _make(CitationVerificationAgent, sc)
        self.multi_model_debate    = MultiModelDebateAgent()   # uses Groq directly
        self.fact_extraction       = _make(FactExtractionAgent, sc)
        self.issue_identification  = _make(LegalIssueIdentificationAgent, sc)
        self.constitution_retrieval= _make(ConstitutionRetrievalAgent, sc)
        self.law_book_retrieval    = _make(LawBookRetrievalAgent, sc)
        self.evidence_ranking      = _make(EvidenceRankingAgent, sc)
        self.legal_principle       = _make(LegalPrincipleAgent, sc)
        self.reasoning             = _make(ReasoningAgent, sc)
        self.cross_examination     = _make(CrossExaminationAgent, sc)
        self.confidence_assessment = _make(ConfidenceAssessmentAgent, sc)
        self.report_generation     = _make(ReportGenerationAgent, sc)
        self.rag                   = get_rag_service()

    async def process_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        results: Dict[str, Any] = {"agent_logs": []}
        doc_text   = case_data.get("document_text", "")
        case_title = case_data.get("title", "Untitled Case")
        case_id    = case_data.get("id", "")
        has_kb     = self.rag.has_legal_kb()

        logger.info("Starting 19-agent workflow", case_id=case_id,
                    provider=self.session_config.get("provider", "fallback"))

        def log(r):
            results["agent_logs"].append(r)

        def ok(r):
            return r.get("status") == "success"

        def get(r, key, default):
            return r["result"].get(key, default) if ok(r) else default

        try:
            # ── Step 1: Ingest case doc ──────────────────────────────
            if doc_text and case_id:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, lambda: self.rag.ingest_case_document(doc_text, case_id, case_title)
                )

            # ── Step 2: Case Intake ──────────────────────────────────
            r = await self.case_intake.execute({"document_text": doc_text, "case_title": case_title})
            log(r)
            if not ok(r):
                raise Exception("Case intake failed")

            ex = r["result"].get("extracted_data", {})
            results["facts"]        = ex.get("facts") or ex.get("Facts") or []
            results["parties"]      = ex.get("parties") or ex.get("Parties") or {}
            results["timeline"]     = ex.get("timeline") or ex.get("Timeline") or []
            results["jurisdiction"] = ex.get("jurisdiction") or ex.get("Jurisdiction") or ""
            results["legal_issues"] = ex.get("legal_issues") or ex.get("Legal Issues") or []
            results["case_type"]    = ex.get("case_type") or ex.get("Case Type") or ""
            results["relief_sought"]= ex.get("relief_sought") or ex.get("Relief Sought") or ""

            # ── Step 3: Fact Extraction ──────────────────────────────
            r = await self.fact_extraction.execute({"document_text": doc_text, "case_title": case_title})
            log(r)
            if ok(r):
                fe = r["result"].get("extracted_facts", {})
                results["unknown_facts"]  = fe.get("unknown_facts", [])
                results["contradictions"] = fe.get("contradictions", [])
                results["claims"]         = fe.get("claims", [])
                if fe.get("established_facts"):
                    results["facts"] = fe["established_facts"]

            # ── Step 4: Legal Issue Identification ───────────────────
            r = await self.issue_identification.execute({
                "facts": results["facts"], "claims": results.get("claims", []),
                "case_type": results["case_type"],
            })
            log(r)
            if ok(r):
                results["possible_violations"] = r["result"].get("possible_violations", [])
                results["applicable_domains"]  = r["result"].get("applicable_domains", [])
                combined = r["result"].get("primary_issues", []) + r["result"].get("secondary_issues", [])
                if combined:
                    results["legal_issues"] = combined

            # ── Steps 5-8: RAG + existing research (all parallel) ────
            r1, r2, r3, r4 = await asyncio.gather(
                self.constitution_retrieval.execute({"legal_issues": results["legal_issues"], "facts": results["facts"]}),
                self.law_book_retrieval.execute({"legal_issues": results["legal_issues"], "case_type": results["case_type"], "facts": results["facts"]}),
                self.statute_research.execute({"legal_issues": results["legal_issues"], "case_type": results["case_type"], "jurisdiction": results["jurisdiction"], "facts": results["facts"]}),
                self.caselaw_retrieval.execute({"legal_issues": results["legal_issues"], "case_type": results["case_type"], "jurisdiction": results["jurisdiction"], "facts": results["facts"]}),
            )
            for r in [r1, r2, r3, r4]:
                log(r)

            results["constitutional_provisions"] = get(r1, "constitutional_provisions", [])
            results["statutory_provisions"]      = get(r2, "statutory_provisions", [])
            results["statutes"]                  = get(r3, "statutes", [])
            results["precedents"]                = get(r4, "precedents", [])

            # Retrieve from case-specific chunks
            case_chunks = []
            loop = asyncio.get_running_loop()
            for issue in results["legal_issues"][:3]:
                chunks = await loop.run_in_executor(
                    None, lambda q=issue: self.rag.retrieve_from_case(q, case_id, top_k=4)
                )
                case_chunks.extend(chunks)

            # ── Step 9: Evidence Ranking ─────────────────────────────
            r = await self.evidence_ranking.execute({
                "constitutional_provisions": results["constitutional_provisions"],
                "statutory_provisions":      results["statutory_provisions"],
                "case_document_chunks":      case_chunks,
                "legal_issues":              results["legal_issues"],
            })
            log(r)
            results["ranked_evidence"]  = get(r, "ranked_evidence", [])
            results["evidence_summary"] = get(r, "evidence_summary", "")

            # ── Step 10: Legal Principles ────────────────────────────
            r = await self.legal_principle.execute({
                "ranked_evidence": results["ranked_evidence"],
                "legal_issues":    results["legal_issues"],
                "case_type":       results["case_type"],
            })
            log(r)
            results["legal_principles"] = get(r, "legal_principles", [])

            # ── Step 11: Reasoning Chain ─────────────────────────────
            r = await self.reasoning.execute({
                "facts": results["facts"], "legal_issues": results["legal_issues"],
                "ranked_evidence": results["ranked_evidence"],
                "legal_principles": results["legal_principles"], "parties": results["parties"],
            })
            log(r)
            results["reasoning_chain"]   = get(r, "reasoning_chain", [])
            results["possible_outcomes"] = get(r, "possible_outcomes", [])

            # ── Steps 12-13: Plaintiff + Defendant (parallel) ────────
            r_p, r_d = await asyncio.gather(
                self.plaintiff_advocate.execute({"facts": results["facts"], "legal_issues": results["legal_issues"],
                    "statutes": results["statutes"], "precedents": results["precedents"],
                    "parties": results["parties"], "relief_sought": results["relief_sought"],
                    "ranked_evidence": results["ranked_evidence"], "legal_principles": results["legal_principles"]}),
                self.defendant_advocate.execute({"facts": results["facts"], "legal_issues": results["legal_issues"],
                    "statutes": results["statutes"], "precedents": results["precedents"],
                    "parties": results["parties"], "plaintiff_arguments": {},
                    "ranked_evidence": results["ranked_evidence"]}),
            )
            log(r_p); log(r_d)
            results["plaintiff_arguments"] = get(r_p, "plaintiff_arguments", {})
            results["defendant_arguments"] = get(r_d, "defendant_arguments", {})

            # ── Step 14: Cross Examination ───────────────────────────
            r = await self.cross_examination.execute({
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "ranked_evidence": results["ranked_evidence"],
            })
            log(r)
            results["plaintiff_challenges"] = get(r, "plaintiff_challenges", [])
            results["defendant_challenges"] = get(r, "defendant_challenges", [])

            # ── Step 15: Judge ───────────────────────────────────────
            r = await self.judge.execute({
                "facts": results["facts"], "legal_issues": results["legal_issues"],
                "statutes": results["statutes"], "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "parties": results["parties"], "ranked_evidence": results["ranked_evidence"],
                "reasoning_chain": results["reasoning_chain"],
            })
            log(r)
            results["judgment"]       = get(r, "judgment", {})
            results["verdict"]        = get(r, "verdict", "")
            results["confidence_score"] = get(r, "confidence_score", 0.0)

            # ── Steps 16-17: Risk + Citation (parallel) ──────────────
            r_ri, r_ci = await asyncio.gather(
                self.risk_analysis.execute({"facts": results["facts"], "legal_issues": results["legal_issues"],
                    "plaintiff_arguments": results["plaintiff_arguments"],
                    "defendant_arguments": results["defendant_arguments"], "judgment": results["judgment"]}),
                self.citation_verification.execute({"statutes": results["statutes"], "precedents": results["precedents"],
                    "plaintiff_arguments": results["plaintiff_arguments"],
                    "defendant_arguments": results["defendant_arguments"]}),
            )
            log(r_ri); log(r_ci)
            results["risk_analysis"]      = get(r_ri, "risk_analysis", {})
            results["plaintiff_strength"] = get(r_ri, "plaintiff_strength", 0.0)
            results["defendant_strength"] = get(r_ri, "defendant_strength", 0.0)
            results["citation_verification"] = get(r_ci, "verification_results", {})

            # ── Step 18: Multi-Model Debate ──────────────────────────
            r = await self.multi_model_debate.execute({
                "facts": results["facts"], "legal_issues": results["legal_issues"],
                "statutes": results["statutes"], "precedents": results["precedents"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "judgment": results["judgment"], "parties": results["parties"],
            })
            log(r)
            if ok(r):
                results["multi_model_debate"] = {
                    "debate_transcript":   r.get("debate_transcript", []),
                    "final_consensus":     r.get("final_consensus", ""),
                    "participating_models": r["result"].get("participating_models", []),
                    "total_rounds":        r["result"].get("total_rounds", 0),
                }
            else:
                results["multi_model_debate"] = {"status": r.get("status","skipped"), "error": r.get("error","")}

            # ── Step 19: Confidence + Report ─────────────────────────
            r = await self.confidence_assessment.execute({
                "ranked_evidence": results["ranked_evidence"],
                "reasoning_chain": results["reasoning_chain"],
                "judgment": results["judgment"],
                "citation_verification": results["citation_verification"],
                "has_legal_kb": has_kb,
            })
            log(r)
            results["confidence_assessment"] = r["result"] if ok(r) else {}

            r = await self.report_generation.execute({
                "case_title": case_title, "parties": results["parties"],
                "facts": results["facts"], "legal_issues": results["legal_issues"],
                "timeline": results["timeline"], "ranked_evidence": results["ranked_evidence"],
                "legal_principles": results["legal_principles"],
                "constitutional_provisions": results["constitutional_provisions"],
                "statutory_provisions": results["statutory_provisions"],
                "plaintiff_arguments": results["plaintiff_arguments"],
                "defendant_arguments": results["defendant_arguments"],
                "plaintiff_challenges": results["plaintiff_challenges"],
                "defendant_challenges": results["defendant_challenges"],
                "reasoning_chain": results["reasoning_chain"],
                "judgment": results["judgment"], "risk_analysis": results["risk_analysis"],
                "multi_model_debate": results["multi_model_debate"],
                "confidence_assessment": results["confidence_assessment"],
                "evidence_summary": results["evidence_summary"],
                "unknown_facts": results.get("unknown_facts", []),
                "contradictions": results.get("contradictions", []),
                "possible_violations": results.get("possible_violations", []),
                "case_type": results["case_type"], "jurisdiction": results["jurisdiction"],
            })
            log(r)
            results["structured_report"] = get(r, "report", {})
            results["has_legal_kb"]      = has_kb
            results["status"]            = "completed"
            logger.info("Workflow completed", case_id=case_id)

        except Exception as e:
            logger.error(f"Workflow error: {e}", case_id=case_id)
            results["status"] = "failed"
            results["error"]  = str(e)

        return results
