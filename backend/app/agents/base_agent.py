from abc import ABC, abstractmethod
from typing import Dict, Any
from groq import Groq
from app.core.config import settings
from app.core.logging import get_logger
import time


class BaseAgent(ABC):
    """
    Base class for all legal reasoning agents.
    Uses Groq (free, fast) as the primary LLM provider.
    Groq supports: llama3-70b-8192, mixtral-8x7b-32768, gemma2-9b-it
    """

    # Primary model for all agents — fast and free on Groq
    PRIMARY_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, agent_name: str, agent_description: str):
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.logger = get_logger(f"agent.{agent_name}")
        self._client = Groq(api_key=settings.GROQ_API_KEY)

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output."""
        pass

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with logging and timing."""
        self.logger.info(f"Starting {self.agent_name}")
        start_time = time.time()

        try:
            result = await self.process(input_data)
            execution_time = time.time() - start_time
            self.logger.info(f"Completed {self.agent_name}", execution_time=execution_time)
            return {
                "agent_name": self.agent_name,
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "reasoning_trace": result.get("reasoning_trace", []),
            }
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Error in {self.agent_name}", error=str(e))
            return {
                "agent_name": self.agent_name,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time,
            }

    async def invoke_llm(self, prompt: str, model: str = None) -> str:
        """Invoke Groq LLM with a prompt. Synchronous Groq client used via executor."""
        import asyncio
        loop = asyncio.get_event_loop()
        chosen_model = model or self.PRIMARY_MODEL

        def _call():
            response = self._client.chat.completions.create(
                model=chosen_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,
            )
            return response.choices[0].message.content.strip()

        return await loop.run_in_executor(None, _call)
