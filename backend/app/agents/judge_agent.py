from typing import Dict, Any
import json
from .base_agent import BaseAgent


class JudgeAgent(BaseAgent):
    """Agent that acts as an impartial judge to render a decision"""
    
    def __init__(self):
        super().__init__(
            agent_name="Judge Agent",
            agent_description="Reviews both sides and produces a detailed legal judgment"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render judicial decision"""
        facts = input_data.get("facts", [])
        legal_issues = input_data.get("legal_issues", [])
        statutes = input_data.get("statutes", [])
        precedents = input_data.get("precedents", [])
        plaintiff_arguments = input_data.get("plaintiff_arguments", {})
        defendant_arguments = input_data.get("defendant_arguments", {})
        parties = input_data.get("parties", {})
        
        prompt = f"""You are an experienced and impartial judge presiding over this case. Review all arguments and evidence, then render a fair and legally sound judgment.

**Case Parties**:
- Plaintiff/Petitioner: {parties.get('plaintiff', 'Plaintiff')}
- Defendant/Respondent: {parties.get('defendant', 'Defendant')}

**Established Facts**:
{json.dumps(facts[:10], indent=2)}

**Legal Issues to Decide**:
{json.dumps(legal_issues, indent=2)}

**Applicable Law**:
{json.dumps([s.get('statute_name', '') for s in statutes[:5]], indent=2)}

**Plaintiff's Position**: {plaintiff_arguments.get('opening_statement', '')}

**Defendant's Position**: {defendant_arguments.get('opening_statement', '')}

**Number of Plaintiff Arguments**: {len(plaintiff_arguments.get('main_arguments', []))}
**Number of Defense Arguments**: {len(defendant_arguments.get('substantive_defenses', []))}

Render a comprehensive judicial opinion in JSON format:

{{
  "case_caption": "Full case caption",
  "court_and_jurisdiction": "Court information",
  "procedural_history": "Brief procedural history",
  "findings_of_fact": [
    {{
      "fact_number": 1,
      "finding": "What the court finds as fact",
      "credibility_assessment": "Assessment of evidence"
    }}
  ],
  "legal_analysis": [
    {{
      "issue": "Legal issue being addressed",
      "applicable_law": "Relevant statutes and precedents",
      "plaintiff_position": "Summary of plaintiff's argument",
      "defendant_position": "Summary of defendant's argument",
      "court_reasoning": "Court's analysis and reasoning",
      "conclusion_on_issue": "How the court decides this issue"
    }}
  ],
  "weighing_of_arguments": {{
    "plaintiff_strengths": ["Strong points in plaintiff's case"],
    "plaintiff_weaknesses": ["Weak points in plaintiff's case"],
    "defendant_strengths": ["Strong points in defendant's case"],
    "defendant_weaknesses": ["Weak points in defendant's case"]
  }},
  "burden_of_proof_analysis": "Whether burden of proof was met",
  "precedent_application": "How precedents apply to this case",
  "policy_considerations": "Any policy considerations",
  "final_decision": {{
    "verdict": "For Plaintiff / For Defendant / Partial",
    "disposition": "Granted / Denied / Dismissed / Remanded",
    "relief_awarded": "What relief, if any, is awarded",
    "reasoning_summary": "Brief summary of key reasoning"
  }},
  "judgment": "Full text of the judgment",
  "confidence_score": 0.0-1.0,
  "dissenting_views": ["Any points where reasonable minds might differ"]
}}

Be thorough, balanced, and legally rigorous. Apply the law impartially to the facts.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            judgment = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                judgment = json.loads(json_match.group())
            else:
                judgment = {
                    "final_decision": {"verdict": "Undetermined", "confidence_score": 0.0},
                    "judgment": "Unable to render judgment due to processing error"
                }
        
        return {
            "judgment": judgment,
            "verdict": judgment.get("final_decision", {}).get("verdict", "Undetermined"),
            "confidence_score": judgment.get("final_decision", {}).get("confidence_score", 0.0),
            "reasoning_trace": [
                "Reviewed all pleadings and arguments",
                "Analyzed credibility and weight of evidence",
                "Applied relevant statutes to established facts",
                "Distinguished and applied case precedents",
                "Evaluated strength of each party's position",
                "Applied burden of proof standard",
                "Rendered impartial judgment based on law and evidence"
            ]
        }
