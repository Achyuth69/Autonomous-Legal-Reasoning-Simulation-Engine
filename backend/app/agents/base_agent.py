from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from app.core.logging import get_logger
import time


class BaseAgent(ABC):
    """Base class for all legal reasoning agents"""
    
    def __init__(self, agent_name: str, agent_description: str):
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.logger = get_logger(f"agent.{agent_name}")
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with logging and timing"""
        self.logger.info(f"Starting {self.agent_name}", input_data=input_data)
        start_time = time.time()
        
        try:
            result = await self.process(input_data)
            execution_time = time.time() - start_time
            
            self.logger.info(
                f"Completed {self.agent_name}",
                execution_time=execution_time,
                status="success"
            )
            
            return {
                "agent_name": self.agent_name,
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "reasoning_trace": result.get("reasoning_trace", [])
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Error in {self.agent_name}",
                error=str(e),
                execution_time=execution_time
            )
            
            return {
                "agent_name": self.agent_name,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time
            }
    
    def create_prompt(self, template: str, **kwargs) -> ChatPromptTemplate:
        """Create a chat prompt template"""
        return ChatPromptTemplate.from_template(template)
    
    async def invoke_llm(self, prompt: str, **kwargs) -> str:
        """Invoke LLM with prompt"""
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.ainvoke(messages)
        return response.content
