from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger
import time


class BaseAgent(ABC):
    """
    Base class for all legal reasoning agents.
    Supports dynamic LLM provider per session (Groq / OpenAI / Gemini).
    Falls back to .env config when no session config provided.
    """

    FALLBACK_PROVIDER = "groq"
    FALLBACK_MODEL    = "llama-3.1-8b-instant"

    def __init__(self, agent_name: str, agent_description: str, session_config: Optional[Dict] = None):
        self.agent_name     = agent_name
        self.agent_description = agent_description
        self.logger         = get_logger(f"agent.{agent_name}")
        self.session_config = session_config or {}

    def _get_llm_config(self) -> tuple[str, str, str]:
        """Return (provider, api_key, model) from session config or .env fallback."""
        sc = self.session_config
        if sc.get("provider") and sc.get("api_key") and sc.get("model"):
            return sc["provider"], sc["api_key"], sc["model"]

        # Fallback to .env
        if settings.GROQ_API_KEY:
            return "groq", settings.GROQ_API_KEY, self.FALLBACK_MODEL
        if settings.GEMINI_API_KEY:
            return "gemini", settings.GEMINI_API_KEY, settings.GEMINI_MODEL
        raise RuntimeError("No LLM configured. Please provide an API key on the setup page.")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Starting {self.agent_name}")
        start = time.time()
        try:
            result = await self.process(input_data)
            exec_time = time.time() - start
            self.logger.info(f"Completed {self.agent_name}", execution_time=exec_time)
            return {
                "agent_name": self.agent_name,
                "status": "success",
                "result": result,
                "execution_time": exec_time,
                "reasoning_trace": result.get("reasoning_trace", []),
            }
        except Exception as e:
            exec_time = time.time() - start
            self.logger.error(f"Error in {self.agent_name}", error=str(e))
            return {
                "agent_name": self.agent_name,
                "status": "failed",
                "error": str(e),
                "execution_time": exec_time,
            }

    async def invoke_llm(self, prompt: str, model: str = None) -> str:
        """Invoke LLM dynamically based on session config with retry logic."""
        import asyncio
        from app.services.llm_router import invoke_llm_sync

        provider, api_key, chosen_model = self._get_llm_config()
        if model:
            chosen_model = model

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: invoke_llm_sync(prompt, provider, api_key, chosen_model)
        )
