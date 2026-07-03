"""Report Generation Agent — produces structured legal reports."""
from typing import Dict, Any
import json
from app.agents.base_agent import BaseAgent


class ReportGenerationAgent(BaseAgent):
    def __init__(self, session_config=None):
        super().__init__("Report Generation Agent",
                         "Generates structured legal analysis reports")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        case_title = input_data.get("case_title", "")
        parties = input_data.get("parties", {})
        facts = input_data.get("facts", [])
        legal_issues = input_data.get("legal_issues", [])
        ranked_evidence = input_data.get("ranked_evidence", [])
        legal_principles = input_data.get("legal_principles", [])
        plaintiff_args = input_data.get("plaintiff_arguments", {})
        defendant_args = input_data.get("defendant_arguments", {})
        reasoning_chain = input_data.get("reasoning_chain", [])
        judgment = input_data.get("judgment", {})
        risk_analysis = input_data.get("risk_analysis", {})
        debate = input_data.get("multi_model_debate", {})
        confidence = input_data.get("confidence_assessment", {})
        timeline = input_data.get("timeline", [])

        sources = list({
            f"{e.get('document','')} {e.get('article','')} {e.get('section','')}".strip()
            for e in ranked_evidence[:15] if e.get("document")
        })

        report = {
            "case_summary": {
                "title": case_title,
                "parties": parties,
                "case_type": input_data.get("case_type", ""),
                "jurisdiction": input_data.get("jurisdiction", ""),
            },
            "timeline": timeline,
            "established_facts": facts,
            "legal_issues": legal_issues,
            "evidence": {
                "total_pieces": len(ranked_evidence),
                "sources": sources,
                "top_evidence": ranked_evidence[:5],
                "evidence_summary": input_data.get("evidence_summary", ""),
            },
            "applicable_law": {
                "constitutional_provisions": input_data.get("constitutional_provisions", []),
                "statutory_provisions": input_data.get("statutory_provisions", []),
                "legal_principles": legal_principles,
            },
            "reasoning_chain": reasoning_chain,
            "plaintiff_arguments": {
                "opening": plaintiff_args.get("opening_statement", ""),
                "main_arguments": plaintiff_args.get("main_arguments", []),
                "conclusion": plaintiff_args.get("conclusion", ""),
            },
            "defendant_arguments": {
                "opening": defendant_args.get("opening_statement", ""),
                "defenses": defendant_args.get("substantive_defenses", []),
                "conclusion": defendant_args.get("conclusion", ""),
            },
            "cross_examination": {
                "plaintiff_challenges": input_data.get("plaintiff_challenges", []),
                "defendant_challenges": input_data.get("defendant_challenges", []),
            },
            "debate_summary": {
                "participating_models": debate.get("participating_models", []),
                "total_rounds": debate.get("total_rounds", 0),
                "final_consensus": debate.get("final_consensus", ""),
            },
            "judicial_analysis": {
                "judgment": judgment.get("judgment", ""),
                "verdict": judgment.get("final_decision", {}).get("verdict", ""),
                "disposition": judgment.get("final_decision", {}).get("disposition", ""),
                "relief_awarded": judgment.get("final_decision", {}).get("relief_awarded", ""),
                "legal_analysis": judgment.get("legal_analysis", []),
                "dissenting_views": judgment.get("dissenting_views", []),
            },
            "risk_assessment": {
                "plaintiff_win_probability": risk_analysis.get("overall_risk_assessment", {}).get("plaintiff_win_probability", 0),
                "defendant_win_probability": risk_analysis.get("overall_risk_assessment", {}).get("defendant_win_probability", 0),
                "case_complexity": risk_analysis.get("overall_risk_assessment", {}).get("case_complexity", ""),
                "settlement_recommended": risk_analysis.get("settlement_recommendations", {}).get("should_settle", False),
            },
            "confidence": {
                "overall": confidence.get("overall_confidence", 0),
                "label": confidence.get("confidence_label", ""),
                "limitations": confidence.get("limitations", []),
                "metrics": confidence.get("metrics", {}),
            },
            "sources_cited": sources,
            "unknown_facts": input_data.get("unknown_facts", []),
            "contradictions": input_data.get("contradictions", []),
            "possible_violations": input_data.get("possible_violations", []),
        }

        return {
            "report": report,
            "reasoning_trace": [
                "Generated comprehensive structured legal report",
                f"Report includes {len(sources)} document sources",
                f"Evidence coverage: {len(ranked_evidence)} pieces",
                "Report ready for display and export",
            ],
        }
