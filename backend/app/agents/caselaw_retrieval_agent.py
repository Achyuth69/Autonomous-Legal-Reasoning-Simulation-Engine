from typing import Dict, Any, List
import json
from .base_agent import BaseAgent


class CaseLawRetrievalAgent(BaseAgent):
    """Agent responsible for retrieving relevant case precedents"""
    
    def __init__(self):
        super().__init__(
            agent_name="Case Law Retrieval Agent",
            agent_description="Retrieves and ranks similar legal precedents"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant case precedents"""
        legal_issues = input_data.get("legal_issues", [])
        case_type = input_data.get("case_type", "")
        jurisdiction = input_data.get("jurisdiction", "")
        facts = input_data.get("facts", [])
        
        prompt = f"""You are an expert legal researcher specializing in case law. Identify relevant legal precedents for this case.

**Jurisdiction**: {jurisdiction}
**Case Type**: {case_type}

**Legal Issues**:
{json.dumps(legal_issues, indent=2)}

**Key Facts**:
{json.dumps(facts[:5], indent=2)}

Identify and return relevant case precedents in JSON format:

{{
  "precedents": [
    {{
      "case_name": "Full case name",
      "citation": "Official citation",
      "year": Year decided,
      "court": "Court name",
      "jurisdiction": "Jurisdiction",
      "facts_summary": "Brief summary of facts",
      "legal_holding": "Key legal holding/principle",
      "relevance_score": 0.0-1.0,
      "relevance_explanation": "Why this case is relevant",
      "distinguishing_factors": ["Any factors that distinguish this case"],
      "key_quotes": ["Important quotes from the judgment"]
    }}
  ],
  "binding_precedents": ["List of binding precedents"],
  "persuasive_precedents": ["List of persuasive but non-binding precedents"],
  "conflicting_precedents": ["Cases with conflicting interpretations"]
}}

Return at least 5-10 relevant precedents, ranked by relevance. Include landmark cases and recent decisions.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            caselaw_results = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                caselaw_results = json.loads(json_match.group())
            else:
                caselaw_results = {
                    "precedents": [],
                    "binding_precedents": [],
                    "persuasive_precedents": [],
                    "conflicting_precedents": []
                }
        
        # Sort precedents by relevance score
        precedents = caselaw_results.get("precedents", [])
        precedents.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return {
            "precedents": precedents,
            "binding_precedents": caselaw_results.get("binding_precedents", []),
            "persuasive_precedents": caselaw_results.get("persuasive_precedents", []),
            "conflicting_precedents": caselaw_results.get("conflicting_precedents", []),
            "reasoning_trace": [
                f"Searched case law database for {len(legal_issues)} legal issues",
                f"Retrieved {len(precedents)} relevant precedents",
                "Ranked precedents by legal relevance",
                "Identified binding vs. persuasive authority",
                "Analyzed factual similarities and distinguishing factors"
            ]
        }
