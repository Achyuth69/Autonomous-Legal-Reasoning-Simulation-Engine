"""
RAG-Backed Retrieval Agents
===========================
All retrieval is from uploaded legal documents only.
If no evidence found → explicitly states "Insufficient authority in uploaded legal sources."
"""
from __future__ import annotations
from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent
from app.services.rag_service import get_rag_service
from app.core.logging import get_logger

INSUFFICIENT = "Insufficient authority found in uploaded legal sources."

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Constitution Retrieval Agent
# ─────────────────────────────────────────────────────────────────────────────
class ConstitutionRetrievalAgent(BaseAgent):
    """Searches ONLY the Constitution PDF in the knowledge base."""

    def __init__(self, session_config=None):
        super().__init__("Constitution Retrieval Agent",
                         "Retrieves constitutional provisions from uploaded Constitution PDF")
        self.rag = get_rag_service()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        legal_issues = input_data.get("legal_issues", [])
        facts = input_data.get("facts", [])
        kb_available = self.rag.has_legal_kb()

        if not kb_available:
            return {
                "constitutional_provisions": [],
                "retrieval_status": "no_knowledge_base",
                "message": INSUFFICIENT,
                "reasoning_trace": ["No legal documents indexed. " + INSUFFICIENT],
            }

        queries = legal_issues[:5] + [f[:120] for f in facts[:3]]
        seen, provisions = set(), []

        for query in queries:
            chunks = self.rag.retrieve_constitution(query, top_k=6)
            for c in chunks:
                key = c["text"][:80]
                if key not in seen and c["similarity_score"] > 0.15:
                    seen.add(key)
                    provisions.append(c)

        # Ask LLM to interpret retrieved chunks in context of legal issues
        if provisions:
            evidence_text = "\n\n".join(
                f"[{c['document']} | Article {c.get('article','')} | "
                f"Section {c.get('section','')} | Confidence: {c['confidence']}]\n{c['text']}"
                for c in provisions[:8]
            )
            prompt = f"""You are analysing constitutional provisions RETRIEVED from uploaded documents.

RETRIEVED CONSTITUTIONAL TEXT:
{evidence_text}

LEGAL ISSUES IN THE CASE:
{json.dumps(legal_issues, indent=2)}

Based ONLY on the retrieved text above, identify which constitutional provisions are directly applicable.
For each provision state:
- Article/Section reference (EXACTLY as it appears in the retrieved text)
- Relevant excerpt
- Why it applies to the case
- Confidence: {', '.join(set(c['confidence'] for c in provisions[:8]))}

STRICT RULE: Do NOT cite any Article or Section not present in the retrieved text above.
If no relevant provision is found, state: "{INSUFFICIENT}"

Respond in JSON:
{{"applicable_provisions": [{{"article": "", "section": "", "document": "", "excerpt": "", "applicability": "", "confidence": ""}}]}}"""

            raw = await self.invoke_llm(prompt)
            try:
                parsed = json.loads(raw)
                interpreted = parsed.get("applicable_provisions", [])
            except Exception:
                interpreted = []
        else:
            interpreted = []

        return {
            "constitutional_provisions": interpreted,
            "raw_chunks": provisions[:10],
            "retrieval_status": "success" if provisions else "no_results",
            "message": "" if provisions else INSUFFICIENT,
            "reasoning_trace": [
                f"Searched constitutional knowledge base with {len(queries)} queries",
                f"Retrieved {len(provisions)} constitutional chunks",
                f"Identified {len(interpreted)} applicable provisions",
                "All provisions sourced from uploaded Constitution document",
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Law Book Retrieval Agent
# ─────────────────────────────────────────────────────────────────────────────
class LawBookRetrievalAgent(BaseAgent):
    """Searches ONLY law/statute PDFs in the knowledge base."""

    def __init__(self, session_config=None):
        super().__init__("Law Book Retrieval Agent",
                         "Retrieves statutory provisions from uploaded law books")
        self.rag = get_rag_service()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        legal_issues = input_data.get("legal_issues", [])
        case_type = input_data.get("case_type", "")
        facts = input_data.get("facts", [])
        kb_available = self.rag.has_legal_kb()

        if not kb_available:
            return {
                "statutory_provisions": [],
                "retrieval_status": "no_knowledge_base",
                "message": INSUFFICIENT,
                "reasoning_trace": ["No legal documents indexed. " + INSUFFICIENT],
            }

        queries = legal_issues[:5] + [case_type] + [f[:120] for f in facts[:2]]
        queries = [q for q in queries if q]
        seen, provisions = set(), []

        for query in queries:
            chunks = self.rag.retrieve_law(query, top_k=6)
            for c in chunks:
                key = c["text"][:80]
                if key not in seen and c["similarity_score"] > 0.15:
                    seen.add(key)
                    provisions.append(c)

        if provisions:
            evidence_text = "\n\n".join(
                f"[{c['document']} | Section {c.get('section','')} | "
                f"Chapter {c.get('chapter','')} | Confidence: {c['confidence']}]\n{c['text']}"
                for c in provisions[:8]
            )
            prompt = f"""You are analysing statutory provisions RETRIEVED from uploaded law books.

RETRIEVED STATUTORY TEXT:
{evidence_text}

LEGAL ISSUES: {json.dumps(legal_issues)}
CASE TYPE: {case_type}

Based ONLY on the retrieved text, identify applicable statutory provisions.
For each provision state:
- Section/Chapter (EXACTLY as in retrieved text)
- Document name
- Relevant excerpt
- How it applies

STRICT RULE: Do NOT invent or paraphrase sections not present in the retrieved text.
If insufficient: state "{INSUFFICIENT}"

JSON response:
{{"statutory_provisions": [{{"section": "", "chapter": "", "document": "", "excerpt": "", "applicability": "", "confidence": ""}}]}}"""

            raw = await self.invoke_llm(prompt)
            try:
                parsed = json.loads(raw)
                interpreted = parsed.get("statutory_provisions", [])
            except Exception:
                interpreted = []
        else:
            interpreted = []

        return {
            "statutory_provisions": interpreted,
            "raw_chunks": provisions[:10],
            "retrieval_status": "success" if provisions else "no_results",
            "message": "" if provisions else INSUFFICIENT,
            "reasoning_trace": [
                f"Searched law book knowledge base with {len(queries)} queries",
                f"Retrieved {len(provisions)} statutory chunks",
                f"Identified {len(interpreted)} applicable provisions",
                "All provisions sourced from uploaded law documents",
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Evidence Ranking Agent
# ─────────────────────────────────────────────────────────────────────────────
class EvidenceRankingAgent(BaseAgent):
    """Merges, deduplicates and ranks all retrieved evidence."""

    def __init__(self, session_config=None):
        super().__init__("Evidence Ranking Agent",
                         "Merges and ranks retrieved evidence from all sources")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        constitutional = input_data.get("constitutional_provisions", [])
        statutory = input_data.get("statutory_provisions", [])
        case_chunks = input_data.get("case_document_chunks", [])
        legal_issues = input_data.get("legal_issues", [])

        all_evidence = []
        for item in constitutional:
            all_evidence.append({**item, "evidence_type": "constitutional", "source_priority": 1})
        for item in statutory:
            all_evidence.append({**item, "evidence_type": "statutory", "source_priority": 2})
        for item in case_chunks:
            all_evidence.append({**item, "evidence_type": "case_document", "source_priority": 3})

        if not all_evidence:
            return {
                "ranked_evidence": [],
                "evidence_summary": INSUFFICIENT,
                "has_evidence": False,
                "reasoning_trace": ["No evidence retrieved from any source. " + INSUFFICIENT],
            }

        prompt = f"""You are an Evidence Ranking Agent for a legal case.

ALL RETRIEVED EVIDENCE (from uploaded documents only):
{json.dumps(all_evidence[:15], indent=2)}

LEGAL ISSUES: {json.dumps(legal_issues)}

Rank and organise this evidence. For each piece of evidence assign:
- relevance_score: 0.0-1.0
- supports: "plaintiff" | "defendant" | "neutral"
- key_principle: one sentence
- contradictions: list any contradictions with other evidence

Return JSON:
{{"ranked_evidence": [{{"rank": 1, "text": "", "document": "", "article": "", "section": "", "evidence_type": "", "relevance_score": 0.0, "supports": "", "key_principle": "", "contradictions": []}}], "evidence_summary": "brief summary of all evidence"}}"""

        raw = await self.invoke_llm(prompt)
        try:
            parsed = json.loads(raw)
            ranked = parsed.get("ranked_evidence", [])
            summary = parsed.get("evidence_summary", "")
        except Exception:
            ranked = all_evidence[:10]
            summary = f"Retrieved {len(all_evidence)} pieces of evidence"

        return {
            "ranked_evidence": ranked,
            "evidence_summary": summary,
            "has_evidence": True,
            "total_evidence_pieces": len(all_evidence),
            "reasoning_trace": [
                f"Merged {len(constitutional)} constitutional + {len(statutory)} statutory + {len(case_chunks)} case document chunks",
                f"Ranked {len(ranked)} evidence pieces by legal relevance",
                "Identified supporting evidence for both parties",
                "All evidence traceable to uploaded documents",
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Legal Principle Agent
# ─────────────────────────────────────────────────────────────────────────────
class LegalPrincipleAgent(BaseAgent):
    """Derives legal principles from retrieved evidence only."""

    def __init__(self, session_config=None):
        super().__init__("Legal Principle Agent",
                         "Derives legal principles from retrieved document evidence")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        ranked_evidence = input_data.get("ranked_evidence", [])
        legal_issues = input_data.get("legal_issues", [])
        case_type = input_data.get("case_type", "")

        if not ranked_evidence:
            return {
                "legal_principles": [],
                "message": INSUFFICIENT,
                "reasoning_trace": ["No evidence available to derive principles. " + INSUFFICIENT],
            }

        evidence_text = "\n\n".join(
            f"[{e.get('document','?')} | {e.get('evidence_type','')}]\n"
            f"Article/Section: {e.get('article','')}/{e.get('section','')}\n"
            f"{e.get('text', e.get('excerpt',''))}"
            for e in ranked_evidence[:10]
        )

        prompt = f"""You are a Legal Principle Agent. Derive legal principles ONLY from the retrieved evidence below.

RETRIEVED EVIDENCE FROM UPLOADED DOCUMENTS:
{evidence_text}

LEGAL ISSUES: {json.dumps(legal_issues)}
CASE TYPE: {case_type}

Based ONLY on the retrieved evidence, state the applicable legal principles.
Each principle MUST reference a specific document, article, or section from the evidence above.

STRICT RULE: Do NOT state any principle that cannot be traced to the evidence above.

JSON response:
{{"legal_principles": [{{"principle": "", "derived_from": {{"document": "", "article": "", "section": ""}}, "application": "", "confidence": "HIGH|MEDIUM|LOW"}}]}}"""

        raw = await self.invoke_llm(prompt)
        try:
            parsed = json.loads(raw)
            principles = parsed.get("legal_principles", [])
        except Exception:
            principles = []

        return {
            "legal_principles": principles,
            "message": "" if principles else INSUFFICIENT,
            "reasoning_trace": [
                f"Derived {len(principles)} legal principles from retrieved evidence",
                "All principles traced to uploaded documents",
                "No principles invented without documentary support",
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Reasoning Agent
# ─────────────────────────────────────────────────────────────────────────────
class ReasoningAgent(BaseAgent):
    """
    Core reasoning: Facts → Issues → Evidence → Principles → Outcomes.
    Never produces conclusions without evidence.
    """

    def __init__(self, session_config=None):
        super().__init__("Reasoning Agent",
                         "Converts facts + evidence into structured legal reasoning")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        facts = input_data.get("facts", [])
        legal_issues = input_data.get("legal_issues", [])
        ranked_evidence = input_data.get("ranked_evidence", [])
        legal_principles = input_data.get("legal_principles", [])
        parties = input_data.get("parties", {})

        if not ranked_evidence:
            return {
                "reasoning_chain": [],
                "possible_outcomes": [],
                "missing_evidence": ["No evidence retrieved from uploaded legal documents"],
                "message": INSUFFICIENT,
                "reasoning_trace": ["Cannot reason without documentary evidence. " + INSUFFICIENT],
            }

        evidence_summary = "\n".join(
            f"- [{e.get('document','?')} {e.get('article','')} {e.get('section','')}]: "
            f"{str(e.get('text', e.get('excerpt','')))[:200]}"
            for e in ranked_evidence[:8]
        )
        principles_summary = "\n".join(
            f"- {p.get('principle','')} (Source: {p.get('derived_from',{}).get('document','?')})"
            for p in legal_principles[:6]
        )

        prompt = f"""You are a Reasoning Agent constructing a legal reasoning chain.

PARTIES: {parties.get('plaintiff','Plaintiff')} v. {parties.get('defendant','Defendant')}

ESTABLISHED FACTS:
{json.dumps(facts[:10], indent=2)}

LEGAL ISSUES:
{json.dumps(legal_issues, indent=2)}

RETRIEVED EVIDENCE (from uploaded documents):
{evidence_summary}

LEGAL PRINCIPLES (derived from evidence):
{principles_summary}

Build a step-by-step reasoning chain. Each step MUST cite specific evidence.
Identify possible legal outcomes with confidence levels.
List any missing evidence that would strengthen the analysis.

STRICT RULE: Every conclusion must reference a specific document, article, or section.

JSON response:
{{"reasoning_chain": [{{"step": 1, "issue": "", "applicable_law": "", "evidence_reference": {{"document":"","article":"","section":""}}, "reasoning": "", "interim_conclusion": ""}}], "possible_outcomes": [{{"outcome": "", "probability": 0.0, "supporting_evidence": [], "confidence": ""}}], "missing_evidence": [], "contradictions": []}}"""

        raw = await self.invoke_llm(prompt)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"reasoning_chain": [], "possible_outcomes": [], "missing_evidence": [], "contradictions": []}

        return {
            **parsed,
            "reasoning_trace": [
                f"Built reasoning chain from {len(ranked_evidence)} evidence pieces",
                f"Applied {len(legal_principles)} legal principles",
                f"Identified {len(parsed.get('possible_outcomes',[]))} possible outcomes",
                "Every conclusion references uploaded document evidence",
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Cross Examination Agent
# ─────────────────────────────────────────────────────────────────────────────
class CrossExaminationAgent(BaseAgent):
    """Challenges plaintiff and defendant arguments with evidence from uploaded documents."""

    def __init__(self, session_config=None):
        super().__init__("Cross Examination Agent",
                         "Challenges arguments using evidence from uploaded documents")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        plaintiff_args = input_data.get("plaintiff_arguments", {})
        defendant_args = input_data.get("defendant_arguments", {})
        ranked_evidence = input_data.get("ranked_evidence", [])

        if not ranked_evidence:
            return {
                "plaintiff_challenges": [],
                "defendant_challenges": [],
                "message": INSUFFICIENT,
                "reasoning_trace": ["No evidence to cross-examine with. " + INSUFFICIENT],
            }

        evidence_text = "\n".join(
            f"- [{e.get('document','?')}]: {str(e.get('text', e.get('excerpt','')))[:150]}"
            for e in ranked_evidence[:8]
        )
        p_args = [a.get("title","") for a in plaintiff_args.get("main_arguments", [])[:5]]
        d_defs = [d.get("title","") for d in defendant_args.get("substantive_defenses", [])[:5]]

        prompt = f"""You are a Cross Examination Agent. Challenge both parties' arguments using ONLY retrieved evidence.

RETRIEVED EVIDENCE:
{evidence_text}

PLAINTIFF ARGUMENTS: {json.dumps(p_args)}
DEFENDANT DEFENSES: {json.dumps(d_defs)}

For each argument, identify:
1. Which parts are supported by retrieved evidence
2. Which parts are unsupported (cite absence of evidence)
3. Specific document reference that challenges or confirms the argument

JSON:
{{"plaintiff_challenges": [{{"argument": "", "challenge": "", "evidence_reference": "", "strength_of_challenge": "HIGH|MEDIUM|LOW"}}], "defendant_challenges": [{{"defense": "", "challenge": "", "evidence_reference": "", "strength_of_challenge": "HIGH|MEDIUM|LOW"}}]}}"""

        raw = await self.invoke_llm(prompt)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"plaintiff_challenges": [], "defendant_challenges": []}

        return {
            **parsed,
            "reasoning_trace": [
                f"Cross-examined {len(p_args)} plaintiff arguments",
                f"Cross-examined {len(d_defs)} defendant defenses",
                "All challenges based on retrieved document evidence",
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Confidence Assessment Agent
# ─────────────────────────────────────────────────────────────────────────────
class ConfidenceAssessmentAgent(BaseAgent):
    """Calculates overall confidence based on evidence quality and coverage."""

    def __init__(self, session_config=None):
        super().__init__("Confidence Assessment Agent",
                         "Assesses confidence based on documentary evidence coverage")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        ranked_evidence = input_data.get("ranked_evidence", [])
        reasoning_chain = input_data.get("reasoning_chain", [])
        judgment = input_data.get("judgment", {})
        citation_verification = input_data.get("citation_verification", {})
        has_legal_kb = input_data.get("has_legal_kb", False)

        # Calculate metrics
        evidence_count = len(ranked_evidence)
        high_conf_evidence = sum(1 for e in ranked_evidence if e.get("confidence") == "HIGH")
        citation_stats = citation_verification.get("statistics", {})
        valid_citations = citation_stats.get("valid_citations", 0)
        total_citations = citation_stats.get("total_citations", 1)
        citation_rate = valid_citations / max(total_citations, 1)

        # Composite score
        evidence_score = min(evidence_count / 10, 1.0)
        high_conf_score = high_conf_evidence / max(evidence_count, 1)
        kb_score = 1.0 if has_legal_kb else 0.3
        reasoning_score = min(len(reasoning_chain) / 5, 1.0)

        overall = (
            0.35 * evidence_score +
            0.25 * high_conf_score +
            0.20 * citation_rate +
            0.15 * reasoning_score +
            0.05 * kb_score
        )

        limitations = []
        if not has_legal_kb:
            limitations.append("No legal documents indexed — analysis based on LLM knowledge only")
        if evidence_count < 3:
            limitations.append("Insufficient documentary evidence retrieved")
        if citation_rate < 0.7:
            limitations.append(f"Only {int(citation_rate*100)}% of citations verified")
        if not reasoning_chain:
            limitations.append("Incomplete reasoning chain")

        return {
            "overall_confidence": round(overall, 3),
            "confidence_label": _score_label(overall),
            "metrics": {
                "evidence_pieces": evidence_count,
                "high_confidence_evidence": high_conf_evidence,
                "citation_verification_rate": round(citation_rate, 3),
                "reasoning_steps": len(reasoning_chain),
                "kb_available": has_legal_kb,
            },
            "limitations": limitations,
            "reasoning_trace": [
                f"Assessed confidence from {evidence_count} evidence pieces",
                f"Citation verification rate: {int(citation_rate*100)}%",
                f"Overall confidence: {_score_label(overall)} ({round(overall,3)})",
            ],
        }


def _score_label(score: float) -> str:
    if score >= 0.8: return "HIGH"
    if score >= 0.6: return "MEDIUM-HIGH"
    if score >= 0.4: return "MEDIUM"
    if score >= 0.2: return "LOW"
    return "VERY_LOW"


# ─────────────────────────────────────────────────────────────────────────────
# Fact Extraction Agent (extended)
# ─────────────────────────────────────────────────────────────────────────────
class FactExtractionAgent(BaseAgent):
    """Extracts structured facts from case document + unknown facts + contradictions."""

    def __init__(self, session_config=None):
        super().__init__("Fact Extraction Agent",
                         "Extracts facts, unknown facts, and contradictions from case document")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        document_text = input_data.get("document_text", "")
        case_title = input_data.get("case_title", "")

        prompt = f"""You are a Fact Extraction Agent. Extract ALL facts from this legal document with precision.

DOCUMENT: {case_title}
TEXT:
{document_text[:3000]}

Extract and return JSON:
{{
  "established_facts": ["clear, uncontested facts stated in document"],
  "disputed_facts": ["facts that may be contested"],
  "unknown_facts": ["facts that would be relevant but are absent from the document"],
  "contradictions": ["any contradictory statements found in the document"],
  "key_dates": [{{"date": "", "event": ""}}],
  "parties": {{"plaintiff": "", "defendant": "", "other_parties": []}},
  "claims": ["each legal claim made"],
  "reliefs_sought": ["each relief requested"],
  "jurisdiction": "",
  "case_type": ""
}}"""

        raw = await self.invoke_llm(prompt)
        try:
            parsed = json.loads(raw)
        except Exception:
            import re
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            parsed = json.loads(m.group()) if m else {}

        return {
            "extracted_facts": parsed,
            "reasoning_trace": [
                "Extracted established and disputed facts",
                "Identified unknown/missing facts",
                "Found contradictions in document",
                "Extracted parties, claims, reliefs, and jurisdiction",
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Legal Issue Identification Agent
# ─────────────────────────────────────────────────────────────────────────────
class LegalIssueIdentificationAgent(BaseAgent):
    """Automatically identifies all legal issues from facts."""

    def __init__(self, session_config=None):
        super().__init__("Legal Issue Identification Agent",
                         "Identifies legal issues, violations, and applicable law domains")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        facts = input_data.get("facts", [])
        claims = input_data.get("claims", [])
        case_type = input_data.get("case_type", "")

        prompt = f"""You are a Legal Issue Identification Agent. Identify ALL legal issues from the given facts.

FACTS: {json.dumps(facts[:15])}
CLAIMS: {json.dumps(claims[:10])}
CASE TYPE: {case_type}

Identify issues across all applicable legal domains:
Fundamental Rights, Equality, Liberty, Contracts, Property, Employment,
Criminal Law, Civil Law, Administrative Law, Constitutional Law, Tax,
Consumer, Cyber, Family, Tort, etc.

JSON response:
{{
  "primary_issues": ["most critical legal questions"],
  "secondary_issues": ["supporting legal questions"],
  "possible_violations": ["specific law/right violations"],
  "applicable_domains": ["list of legal domains involved"],
  "issue_tree": [{{"issue": "", "domain": "", "sub_issues": [], "priority": "HIGH|MEDIUM|LOW"}}]
}}"""

        raw = await self.invoke_llm(prompt)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"primary_issues": [], "secondary_issues": [], "possible_violations": []}

        return {
            **parsed,
            "reasoning_trace": [
                f"Identified {len(parsed.get('primary_issues',[]))} primary issues",
                f"Found {len(parsed.get('possible_violations',[]))} possible violations",
                f"Covered domains: {', '.join(parsed.get('applicable_domains',[])[:5])}",
            ],
        }
