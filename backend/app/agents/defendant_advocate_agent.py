from typing import Dict, Any
import json
from .base_agent import BaseAgent


class DefendantAdvocateAgent(BaseAgent):
    """Agent that generates arguments supporting the defendant/respondent"""
    
    def __init__(self):
        super().__init__(
            agent_name="Defendant Advocate Agent",
            agent_description="Generates comprehensive counterarguments defending the defendant's position"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate defendant counterarguments"""
        facts = input_data.get("facts", [])
        legal_issues = input_data.get("legal_issues", [])
        statutes = input_data.get("statutes", [])
        precedents = input_data.get("precedents", [])
        parties = input_data.get("parties", {})
        plaintiff_arguments = input_data.get("plaintiff_arguments", {})
        
        prompt = f"""You are a skilled defense attorney representing the defendant/respondent. Build the strongest possible defense against the plaintiff's claims.

**Your Client**: {parties.get('defendant', 'Defendant')}
**Opposing Party**: {parties.get('plaintiff', 'Plaintiff')}

**Facts of the Case**:
{json.dumps(facts, indent=2)}

**Legal Issues**:
{json.dumps(legal_issues, indent=2)}

**Applicable Statutes**:
{json.dumps([s.get('statute_name', '') for s in statutes[:5]], indent=2)}

**Plaintiff's Main Arguments** (to be countered):
{json.dumps([a.get('title', '') for a in plaintiff_arguments.get('main_arguments', [])[:5]], indent=2)}

Construct a comprehensive defense in JSON format:

{{
  "opening_statement": "Persuasive opening defense summary",
  "threshold_defenses": ["Procedural or jurisdictional defenses"],
  "substantive_defenses": [
    {{
      "defense_number": 1,
      "title": "Defense title",
      "counter_claim": "The defensive legal claim",
      "supporting_facts": ["Facts supporting this defense"],
      "legal_basis": "Statutory or case law basis",
      "citations": ["Specific citations"],
      "reasoning": "Step-by-step defensive reasoning",
      "strength": "high/medium/low"
    }}
  ],
  "refutation_of_plaintiff_arguments": [
    {{
      "plaintiff_argument": "Argument being refuted",
      "refutation": "How this argument fails legally or factually",
      "supporting_citations": []
    }}
  ],
  "affirmative_defenses": ["Legal affirmative defenses"],
  "burden_of_proof_arguments": ["Arguments about plaintiff's failure to meet burden of proof"],
  "policy_arguments": ["Public policy considerations favoring defendant"],
  "conclusion": "Strong concluding defense",
  "relief_requested": "What outcome the defendant seeks"
}}

Be thorough, legally sound, and address each of the plaintiff's arguments directly.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            defense_arguments = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                defense_arguments = json.loads(json_match.group())
            else:
                defense_arguments = {
                    "opening_statement": "",
                    "substantive_defenses": [],
                    "conclusion": ""
                }
        
        return {
            "defendant_arguments": defense_arguments,
            "defense_count": len(defense_arguments.get("substantive_defenses", [])),
            "reasoning_trace": [
                "Analyzed plaintiff's claims and arguments",
                "Identified weaknesses in plaintiff's case",
                "Developed substantive defenses",
                "Formulated threshold and procedural objections",
                "Applied favorable precedents to defense",
                "Constructed affirmative defense arguments"
            ]
        }
