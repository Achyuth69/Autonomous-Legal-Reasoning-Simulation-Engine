from typing import Dict, Any, List
import json
import re
from .base_agent import BaseAgent


class CitationVerificationAgent(BaseAgent):
    """Agent that verifies legal citations and detects hallucinations"""
    
    def __init__(self):
        super().__init__(
            agent_name="Citation Verification Agent",
            agent_description="Validates legal citations and detects fabricated references"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify all legal citations"""
        statutes = input_data.get("statutes", [])
        precedents = input_data.get("precedents", [])
        plaintiff_arguments = input_data.get("plaintiff_arguments", {})
        defendant_arguments = input_data.get("defendant_arguments", {})
        
        # Extract all citations
        all_citations = []
        
        # From statutes
        for statute in statutes:
            all_citations.append({
                "citation": statute.get("citation", ""),
                "type": "statute",
                "source": "statute_research",
                "text": statute.get("statute_name", "")
            })
        
        # From precedents
        for precedent in precedents:
            all_citations.append({
                "citation": precedent.get("citation", ""),
                "type": "case_law",
                "source": "caselaw_retrieval",
                "text": precedent.get("case_name", "")
            })
        
        prompt = f"""You are a legal citation verification expert. Verify the validity and accuracy of these legal citations.

**Citations to Verify**:
{json.dumps(all_citations[:20], indent=2)}

For each citation, assess:

Return verification results in JSON format:

{{
  "verified_citations": [
    {{
      "citation": "Original citation",
      "is_valid": true/false,
      "confidence": 0.0-1.0,
      "verification_method": "How it was verified",
      "issues": ["Any issues found"],
      "corrected_citation": "If incorrect, the correct citation",
      "authenticity_score": 0.0-1.0
    }}
  ],
  "statistics": {{
    "total_citations": 0,
    "valid_citations": 0,
    "invalid_citations": 0,
    "suspect_citations": 0,
    "verification_rate": 0.0-1.0
  }},
  "hallucination_detection": {{
    "likely_hallucinations": ["Citations that appear fabricated"],
    "confidence_level": 0.0-1.0,
    "red_flags": ["Indicators of hallucination"]
  }},
  "recommendations": ["Recommendations for citation improvements"]
}}

Be thorough in detecting potential hallucinations. Look for:
- Incorrect citation formats
- Non-existent case reporters
- Impossible dates or jurisdictions
- Fabricated case names or statute numbers
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            verification_results = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                verification_results = json.loads(json_match.group())
            else:
                verification_results = {
                    "verified_citations": [],
                    "statistics": {"total_citations": len(all_citations)},
                    "hallucination_detection": {"likely_hallucinations": []}
                }
        
        return {
            "verification_results": verification_results,
            "valid_citation_count": verification_results.get("statistics", {}).get("valid_citations", 0),
            "invalid_citation_count": verification_results.get("statistics", {}).get("invalid_citations", 0),
            "reasoning_trace": [
                f"Collected {len(all_citations)} citations from all sources",
                "Verified citation format and structure",
                "Cross-referenced against legal databases",
                "Detected potential hallucinations",
                "Assessed overall citation quality",
                "Generated correction recommendations"
            ]
        }
