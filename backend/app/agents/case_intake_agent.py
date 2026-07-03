from typing import Dict, Any
import json
from .base_agent import BaseAgent


class CaseIntakeAgent(BaseAgent):
    """Agent responsible for extracting structured information from legal documents"""
    
    def __init__(self):
        super().__init__(
            agent_name="Case Intake Agent",
            agent_description="Extracts facts, parties, timeline, jurisdiction, and legal issues from legal documents"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured information from case document"""
        document_text = input_data.get("document_text", "")
        case_title = input_data.get("case_title", "Untitled Case")
        
        prompt = f"""You are a legal case intake specialist. Analyze the following legal document and extract structured information.

Document Title: {case_title}

Document Content:
{document_text}

Extract and return the following information in JSON format:

1. **Facts**: List all relevant facts mentioned in the document (as array of strings)
2. **Parties**: Identify all parties involved with their roles (plaintiff, defendant, petitioner, respondent, etc.)
3. **Timeline**: Extract chronological events with dates (array of {{date, event}})
4. **Jurisdiction**: Identify the jurisdiction (country, state, court level)
5. **Legal Issues**: Identify the primary legal questions or issues raised
6. **Case Type**: Classify the case (civil, criminal, constitutional, contract, tort, etc.)
7. **Relief Sought**: What is the plaintiff/petitioner asking for?
8. **Key Evidence**: List key pieces of evidence mentioned

Return ONLY a valid JSON object with these fields. Be thorough and precise.
"""
        
        response = await self.invoke_llm(prompt)
        
        # Parse JSON response
        try:
            extracted_data = json.loads(response)
        except json.JSONDecodeError:
            # If LLM doesn't return valid JSON, try to extract it
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                extracted_data = {
                    "facts": [],
                    "parties": {},
                    "timeline": [],
                    "jurisdiction": "Unknown",
                    "legal_issues": [],
                    "case_type": "Unknown",
                    "relief_sought": "Not specified",
                    "key_evidence": []
                }
        
        return {
            "extracted_data": extracted_data,
            "reasoning_trace": [
                "Analyzed document structure and content",
                "Identified parties and their roles",
                "Extracted chronological timeline of events",
                "Determined jurisdiction and case type",
                "Identified core legal issues and relief sought"
            ]
        }
