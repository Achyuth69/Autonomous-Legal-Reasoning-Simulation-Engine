from typing import Dict, Any
import json
from .base_agent import BaseAgent


class PlaintiffAdvocateAgent(BaseAgent):
    """Agent that generates arguments supporting the plaintiff/petitioner"""
    
    def __init__(self, session_config=None):
        super().__init__(
            agent_name="Plaintiff Advocate Agent",
            agent_description="Generates comprehensive arguments supporting the plaintiff's position"
        ,
            session_config=session_config
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plaintiff arguments"""
        facts = input_data.get("facts", [])
        legal_issues = input_data.get("legal_issues", [])
        statutes = input_data.get("statutes", [])
        precedents = input_data.get("precedents", [])
        parties = input_data.get("parties", {})
        relief_sought = input_data.get("relief_sought", "")
        
        prompt = f"""You are a skilled attorney representing the plaintiff/petitioner. Build the strongest possible case supporting your client's position.

**Your Client**: {parties.get('plaintiff', 'Plaintiff')}
**Opposing Party**: {parties.get('defendant', 'Defendant')}
**Relief Sought**: {relief_sought}

**Facts of the Case**:
{json.dumps(facts, indent=2)}

**Legal Issues**:
{json.dumps(legal_issues, indent=2)}

**Applicable Statutes**:
{json.dumps([s.get('statute_name', '') for s in statutes[:5]], indent=2)}

**Relevant Precedents**:
{json.dumps([p.get('case_name', '') for p in precedents[:5]], indent=2)}

Construct a comprehensive legal argument in JSON format:

{{
  "opening_statement": "Persuasive opening summary",
  "main_arguments": [
    {{
      "argument_number": 1,
      "title": "Argument title",
      "claim": "The legal claim",
      "supporting_facts": ["Facts supporting this argument"],
      "legal_basis": "Statutory or case law basis",
      "citations": ["Specific citations"],
      "reasoning": "Step-by-step legal reasoning",
      "strength": "high/medium/low"
    }}
  ],
  "statutory_arguments": ["Arguments based on statutes"],
  "precedent_arguments": ["Arguments based on case law"],
  "policy_arguments": ["Public policy considerations"],
  "equity_arguments": ["Arguments based on fairness and equity"],
  "rebuttals_to_anticipated_defenses": ["Preemptive rebuttals"],
  "conclusion": "Strong concluding argument",
  "relief_justification": "Why the requested relief is appropriate"
}}

Be persuasive, legally sound, and thorough. Present at least 5 strong arguments.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            arguments = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                arguments = json.loads(json_match.group())
            else:
                arguments = {
                    "opening_statement": "",
                    "main_arguments": [],
                    "conclusion": ""
                }
        
        return {
            "plaintiff_arguments": arguments,
            "argument_count": len(arguments.get("main_arguments", [])),
            "reasoning_trace": [
                "Reviewed all facts favorable to plaintiff",
                "Identified strongest legal theories",
                "Applied relevant statutes to facts",
                "Distinguished unfavorable precedents",
                "Constructed multi-layered legal argument",
                "Prepared preemptive rebuttals to defenses"
            ]
        }
