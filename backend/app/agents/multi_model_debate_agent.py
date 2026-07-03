from typing import Dict, Any, List
import json
import asyncio
from groq import Groq
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MultiModelDebateAgent:
    """
    Agent that orchestrates a debate between multiple Groq AI models.
    Each model analyzes the case from different perspectives and debates 
    to reach a consensus conclusion.
    """
    
    def __init__(self):
        self.agent_name = "Multi-Model Debate Agent"
        self.logger = get_logger(f"agent.{self.agent_name}")
        
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your-groq-api-key-here":
            self.logger.warning("Groq API key not configured. Debate feature will be unavailable.")
            self.client = None
            self.models = []
        else:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.models = [m.strip() for m in settings.GROQ_MODELS.split(",")]

        # Map friendly names
        self._name_map = {
            "llama-3.3-70b-versatile": "Llama 3.3 70B",
            "llama-3.1-8b-instant":    "Llama 3.1 8B",
            "llama3-70b-8192":         "Llama 3 70B",
            "mixtral-8x7b-32768":      "Mixtral 8x7B",
            "gemma2-9b-it":            "Gemma 2 9B",
        }
        
        self.debate_rounds = settings.GROQ_DEBATE_ROUNDS
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the multi-model debate"""
        if not self.client:
            return {
                "agent_name": self.agent_name,
                "status": "skipped",
                "error": "Groq API key not configured",
                "debate_transcript": [],
                "final_consensus": "Debate unavailable - Groq API key not configured"
            }
        
        import time
        start_time = time.time()
        
        try:
            result = await self.conduct_debate(input_data)
            execution_time = time.time() - start_time
            
            return {
                "agent_name": self.agent_name,
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "debate_transcript": result.get("debate_transcript", []),
                "final_consensus": result.get("final_consensus", "")
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Error in debate: {str(e)}")
            
            return {
                "agent_name": self.agent_name,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def conduct_debate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct multi-round debate between models"""
        
        # Extract case information
        facts = input_data.get("facts", [])
        legal_issues = input_data.get("legal_issues", [])
        statutes = input_data.get("statutes", [])
        precedents = input_data.get("precedents", [])
        plaintiff_args = input_data.get("plaintiff_arguments", {})
        defendant_args = input_data.get("defendant_arguments", {})
        judgment = input_data.get("judgment", {})
        parties = input_data.get("parties", {})
        
        # Prepare case summary
        case_summary = self._prepare_case_summary(
            facts, legal_issues, statutes, precedents,
            plaintiff_args, defendant_args, judgment, parties
        )
        
        debate_transcript = []
        model_positions = {}
        
        self.logger.info(f"Starting {self.debate_rounds}-round debate with models: {', '.join(self.models)}")
        
        # Conduct debate rounds
        for round_num in range(1, self.debate_rounds + 1):
            self.logger.info(f"Round {round_num}/{self.debate_rounds}")
            
            round_arguments = []
            
            # Each model presents their analysis
            for i, model in enumerate(self.models):
                model_name = self._get_model_name(model)
                
                # Build context from previous rounds
                context = self._build_debate_context(debate_transcript, round_num)
                
                # Generate model's argument
                argument = await self._get_model_argument(
                    model, 
                    case_summary, 
                    context, 
                    round_num,
                    model_name
                )
                
                round_arguments.append({
                    "model": model_name,
                    "model_id": model,
                    "round": round_num,
                    "argument": argument,
                    "timestamp": f"Round {round_num}"
                })
                
                model_positions[model_name] = argument
                
                self.logger.info(f"{model_name} presented argument in round {round_num}")
            
            debate_transcript.extend(round_arguments)
            
            # Add brief pause between rounds for rate limiting
            if round_num < self.debate_rounds:
                await asyncio.sleep(0.5)
        
        # Generate final consensus
        final_consensus = await self._generate_consensus(
            case_summary,
            debate_transcript,
            model_positions
        )
        
        return {
            "debate_transcript": debate_transcript,
            "model_positions": model_positions,
            "final_consensus": final_consensus,
            "participating_models": [self._get_model_name(m) for m in self.models],
            "total_rounds": self.debate_rounds,
            "reasoning_trace": [
                f"Initiated multi-model debate with {len(self.models)} models",
                f"Conducted {self.debate_rounds} rounds of argument exchange",
                "Models challenged each other's reasoning",
                "Identified areas of agreement and disagreement",
                "Synthesized final consensus opinion"
            ]
        }
    
    def _prepare_case_summary(self, facts, legal_issues, statutes, precedents,
                               plaintiff_args, defendant_args, judgment, parties) -> str:
        """Prepare a comprehensive case summary for debate"""
        
        summary_parts = ["# CASE SUMMARY FOR ANALYSIS\n"]
        
        if parties:
            summary_parts.append(f"**Parties**: {parties.get('plaintiff', 'Plaintiff')} v. {parties.get('defendant', 'Defendant')}\n")
        
        if facts:
            summary_parts.append(f"\n## Established Facts ({len(facts)} facts)")
            for i, fact in enumerate(facts[:10], 1):
                summary_parts.append(f"{i}. {fact}")
        
        if legal_issues:
            summary_parts.append(f"\n## Legal Issues ({len(legal_issues)} issues)")
            for i, issue in enumerate(legal_issues, 1):
                summary_parts.append(f"{i}. {issue}")
        
        if statutes:
            summary_parts.append(f"\n## Applicable Statutes ({len(statutes)} statutes)")
            for i, statute in enumerate(statutes[:5], 1):
                summary_parts.append(f"{i}. {statute.get('statute_name', 'Unknown')} - {statute.get('citation', '')}")
        
        if precedents:
            summary_parts.append(f"\n## Relevant Precedents ({len(precedents)} cases)")
            for i, precedent in enumerate(precedents[:5], 1):
                summary_parts.append(f"{i}. {precedent.get('case_name', 'Unknown')} ({precedent.get('year', 'N/A')})")
        
        if plaintiff_args and plaintiff_args.get('main_arguments'):
            summary_parts.append(f"\n## Plaintiff's Position")
            summary_parts.append(f"Opening: {plaintiff_args.get('opening_statement', 'N/A')}")
            summary_parts.append(f"Arguments: {len(plaintiff_args.get('main_arguments', []))} main arguments presented")
        
        if defendant_args and defendant_args.get('substantive_defenses'):
            summary_parts.append(f"\n## Defendant's Position")
            summary_parts.append(f"Opening: {defendant_args.get('opening_statement', 'N/A')}")
            summary_parts.append(f"Defenses: {len(defendant_args.get('substantive_defenses', []))} defenses presented")
        
        if judgment and judgment.get('final_decision'):
            verdict = judgment['final_decision'].get('verdict', 'Undetermined')
            summary_parts.append(f"\n## Initial Judgment: {verdict}")
        
        return "\n".join(summary_parts)
    
    def _build_debate_context(self, transcript: List[Dict], current_round: int) -> str:
        """Build context from previous debate rounds"""
        if current_round == 1 or not transcript:
            return "This is the first round. Provide your initial analysis of the case."
        
        context_parts = [f"\n## Previous Debate Rounds\n"]
        
        for entry in transcript:
            if entry['round'] < current_round:
                context_parts.append(
                    f"**{entry['model']} (Round {entry['round']})**:\n{entry['argument'][:300]}...\n"
                )
        
        context_parts.append(
            f"\n**Your task for Round {current_round}**: "
            f"Respond to the arguments above. Challenge weak points, "
            f"reinforce strong points, and refine your position based on the debate so far."
        )
        
        return "\n".join(context_parts)
    
    async def _get_model_argument(self, model: str, case_summary: str, 
                                   context: str, round_num: int, model_name: str) -> str:
        """Get argument from a specific model"""
        
        prompt = f"""You are {model_name}, an expert AI legal analyst participating in a multi-model debate about a legal case.

{case_summary}

{context}

Your role in this debate:
- Provide rigorous legal analysis from your unique perspective
- Challenge arguments from other models if you disagree
- Acknowledge strong points made by others
- Focus on legal reasoning, precedent, and statutory interpretation
- Be concise but thorough (300-500 words)

Round {round_num} Instructions:
{'Provide your initial analysis of the case. What is your position on the verdict and why?' if round_num == 1 else 'Respond to previous arguments. Refine your position based on the debate.'}

Provide your argument:"""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1024,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            self.logger.error(f"Error getting argument from {model}: {str(e)}")
            return f"[Error: Could not get response from {model_name}]"
    
    async def _generate_consensus(self, case_summary: str, 
                                   transcript: List[Dict],
                                   model_positions: Dict[str, str]) -> str:
        """Generate final consensus from all model arguments"""
        
        # Use the first model to synthesize consensus
        synthesis_model = self.models[0]
        
        debate_summary = "\n\n".join([
            f"**{entry['model']} (Round {entry['round']})**:\n{entry['argument']}"
            for entry in transcript
        ])
        
        prompt = f"""You are synthesizing the conclusions from a multi-model legal debate.

{case_summary}

## Complete Debate Transcript:

{debate_summary}

## Your Task:

Synthesize a final consensus opinion that:
1. Identifies points of agreement among all models
2. Addresses points of disagreement and explains which view is more legally sound
3. Provides a clear final verdict with reasoning
4. Acknowledges the strength of arguments on both sides
5. Delivers a balanced, legally rigorous conclusion

Format your consensus as a judicial opinion with clear sections.

Generate the final consensus opinion (500-800 words):"""
        
        try:
            response = self.client.chat.completions.create(
                model=synthesis_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            self.logger.error(f"Error generating consensus: {str(e)}")
            return "Error generating final consensus. Please review individual model arguments above."
    
    def _get_model_name(self, model_id: str) -> str:
        """Get friendly name for model"""
        return self._name_map.get(model_id, model_id)
