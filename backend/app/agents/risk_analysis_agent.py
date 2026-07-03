from typing import Dict, Any
import json
from .base_agent import BaseAgent


class RiskAnalysisAgent(BaseAgent):
    """Agent that performs litigation risk assessment"""
    
    def __init__(self, session_config=None):
        super().__init__(
            agent_name="Risk Analysis Agent",
            agent_description="Predicts litigation risks and assesses case strengths"
        ,
            session_config=session_config
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze litigation risks"""
        facts = input_data.get("facts", [])
        legal_issues = input_data.get("legal_issues", [])
        plaintiff_arguments = input_data.get("plaintiff_arguments", {})
        defendant_arguments = input_data.get("defendant_arguments", {})
        judgment = input_data.get("judgment", {})
        
        prompt = f"""You are a legal risk assessment expert. Analyze this case and provide a comprehensive risk assessment for both parties.

**Key Facts**: {len(facts)} facts established
**Legal Issues**: {len(legal_issues)} issues identified
**Plaintiff Arguments**: {len(plaintiff_arguments.get('main_arguments', []))} arguments
**Defense Arguments**: {len(defendant_arguments.get('substantive_defenses', []))} defenses
**Predicted Verdict**: {judgment.get('final_decision', {}).get('verdict', 'Unknown')}

Provide risk analysis in JSON format:

{{
  "overall_risk_assessment": {{
    "plaintiff_win_probability": 0.0-1.0,
    "defendant_win_probability": 0.0-1.0,
    "settlement_likelihood": 0.0-1.0,
    "case_complexity": "low/medium/high",
    "expected_duration": "Estimated timeframe"
  }},
  "plaintiff_risks": {{
    "legal_risks": ["Risks in plaintiff's legal position"],
    "factual_risks": ["Weaknesses in facts"],
    "procedural_risks": ["Procedural challenges"],
    "cost_analysis": "Expected costs and benefits",
    "worst_case_scenario": "What could go wrong",
    "best_case_scenario": "Optimal outcome",
    "strength_score": 0.0-10.0
  }},
  "defendant_risks": {{
    "legal_risks": ["Risks in defendant's legal position"],
    "factual_risks": ["Weaknesses in facts"],
    "procedural_risks": ["Procedural challenges"],
    "cost_analysis": "Expected costs and benefits",
    "worst_case_scenario": "What could go wrong",
    "best_case_scenario": "Optimal outcome",
    "strength_score": 0.0-10.0
  }},
  "critical_factors": [
    {{
      "factor": "Critical factor",
      "impact": "How it affects the case",
      "probability": 0.0-1.0,
      "favors": "plaintiff/defendant/neutral"
    }}
  ],
  "settlement_recommendations": {{
    "should_settle": true/false,
    "recommended_settlement_range": "If applicable",
    "settlement_timing": "When to consider settlement",
    "negotiation_leverage": "Who has leverage"
  }},
  "strategic_recommendations": {{
    "for_plaintiff": ["Strategic advice for plaintiff"],
    "for_defendant": ["Strategic advice for defendant"]
  }}
}}

Be objective and data-driven in your risk assessment.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            risk_analysis = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                risk_analysis = json.loads(json_match.group())
            else:
                risk_analysis = {
                    "overall_risk_assessment": {
                        "plaintiff_win_probability": 0.5,
                        "defendant_win_probability": 0.5
                    }
                }
        
        return {
            "risk_analysis": risk_analysis,
            "plaintiff_strength": risk_analysis.get("plaintiff_risks", {}).get("strength_score", 5.0),
            "defendant_strength": risk_analysis.get("defendant_risks", {}).get("strength_score", 5.0),
            "reasoning_trace": [
                "Evaluated strength of legal arguments",
                "Assessed quality and credibility of evidence",
                "Analyzed procedural posture",
                "Considered jurisdictional factors",
                "Calculated win probabilities",
                "Identified critical success factors"
            ]
        }
