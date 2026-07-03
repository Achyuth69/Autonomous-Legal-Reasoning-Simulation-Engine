import pytest
from unittest.mock import AsyncMock, patch
from app.agents.case_intake_agent import CaseIntakeAgent
from app.agents.statute_research_agent import StatuteResearchAgent
from app.agents.plaintiff_advocate_agent import PlaintiffAdvocateAgent


@pytest.mark.asyncio
async def test_case_intake_agent():
    """Test case intake agent extracts information"""
    agent = CaseIntakeAgent()
    
    mock_response = '''
    {
        "facts": ["Plaintiff was injured on January 15, 2023", "Defendant failed to maintain safe premises"],
        "parties": {"plaintiff": "John Doe", "defendant": "ABC Corporation"},
        "timeline": [{"date": "2023-01-15", "event": "Injury occurred"}],
        "jurisdiction": "California, US",
        "legal_issues": ["Negligence", "Premises liability"],
        "case_type": "civil",
        "relief_sought": "Damages for personal injury",
        "key_evidence": ["Medical records", "Witness testimony"]
    }
    '''
    
    with patch.object(agent, 'invoke_llm', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_response
        
        result = await agent.process({
            "document_text": "Test legal document",
            "case_title": "Test Case"
        })
        
        assert "extracted_data" in result
        assert "reasoning_trace" in result
        assert len(result["reasoning_trace"]) > 0


@pytest.mark.asyncio
async def test_plaintiff_advocate_agent():
    """Test plaintiff advocate generates arguments"""
    agent = PlaintiffAdvocateAgent()
    
    mock_response = '''
    {
        "opening_statement": "The evidence clearly establishes liability",
        "main_arguments": [
            {
                "argument_number": 1,
                "title": "Defendant's negligence",
                "claim": "Defendant failed in duty of care",
                "supporting_facts": ["Hazardous condition existed"],
                "legal_basis": "Negligence law",
                "citations": ["Brown v. Smith (2020)"],
                "reasoning": "Step by step analysis",
                "strength": "high"
            }
        ],
        "conclusion": "Judgment should be for plaintiff"
    }
    '''
    
    with patch.object(agent, 'invoke_llm', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_response
        
        result = await agent.process({
            "facts": ["Fact 1", "Fact 2"],
            "legal_issues": ["Negligence"],
            "statutes": [],
            "precedents": [],
            "parties": {"plaintiff": "John Doe", "defendant": "ABC Corp"},
            "relief_sought": "Damages"
        })
        
        assert "plaintiff_arguments" in result
        assert "argument_count" in result


@pytest.mark.asyncio
async def test_agent_execute_returns_metadata():
    """Test that execute() wraps results with agent metadata"""
    agent = CaseIntakeAgent()
    
    mock_result = {
        "extracted_data": {"facts": [], "parties": {}},
        "reasoning_trace": ["Analyzed document"]
    }
    
    with patch.object(agent, 'process', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = mock_result
        
        result = await agent.execute({"document_text": "test", "case_title": "test"})
        
        assert result["agent_name"] == "Case Intake Agent"
        assert result["status"] == "success"
        assert "execution_time" in result


@pytest.mark.asyncio
async def test_agent_handles_failure():
    """Test that execute() handles errors gracefully"""
    agent = CaseIntakeAgent()
    
    with patch.object(agent, 'process', new_callable=AsyncMock) as mock_process:
        mock_process.side_effect = Exception("LLM connection error")
        
        result = await agent.execute({"document_text": "test"})
        
        assert result["status"] == "failed"
        assert "error" in result
