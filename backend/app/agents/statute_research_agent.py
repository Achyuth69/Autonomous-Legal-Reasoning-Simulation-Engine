from typing import Dict, Any, List
import json
from .base_agent import BaseAgent


class StatuteResearchAgent(BaseAgent):
    """Agent responsible for identifying applicable statutes and legal provisions"""
    
    def __init__(self):
        super().__init__(
            agent_name="Statute Research Agent",
            agent_description="Identifies relevant statutes, regulations, and constitutional provisions"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research applicable statutes based on legal issues"""
        legal_issues = input_data.get("legal_issues", [])
        case_type = input_data.get("case_type", "")
        jurisdiction = input_data.get("jurisdiction", "")
        facts = input_data.get("facts", [])
        
        prompt = f"""You are an expert legal researcher specializing in statutory law. Based on the following case information, identify all applicable statutes, regulations, and legal provisions.

**Jurisdiction**: {jurisdiction}
**Case Type**: {case_type}

**Legal Issues**:
{json.dumps(legal_issues, indent=2)}

**Key Facts**:
{json.dumps(facts[:5], indent=2)}

Identify and return the following in JSON format:

1. **applicable_statutes**: Array of relevant statutes, each containing:
   - statute_name: Full name of the statute
   - citation: Official citation
   - section: Specific section(s) applicable
   - text: Key text of the provision
   - relevance: Why this statute applies to the case
   - type: "constitution", "statute", "regulation", "code"

2. **constitutional_provisions**: Any constitutional provisions that apply

3. **regulatory_framework**: Relevant regulatory provisions

4. **legal_principles**: Established legal principles or doctrines that apply

Return a valid JSON object. Be comprehensive and cite specific provisions.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            research_results = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                research_results = json.loads(json_match.group())
            else:
                research_results = {
                    "applicable_statutes": [],
                    "constitutional_provisions": [],
                    "regulatory_framework": [],
                    "legal_principles": []
                }
        
        return {
            "statutes": research_results.get("applicable_statutes", []),
            "constitutional_provisions": research_results.get("constitutional_provisions", []),
            "regulatory_framework": research_results.get("regulatory_framework", []),
            "legal_principles": research_results.get("legal_principles", []),
            "reasoning_trace": [
                f"Analyzed {len(legal_issues)} legal issues",
                "Researched applicable statutes and regulations",
                f"Identified {len(research_results.get('applicable_statutes', []))} relevant statutes",
                "Reviewed constitutional provisions",
                "Compiled comprehensive statutory framework"
            ]
        }
