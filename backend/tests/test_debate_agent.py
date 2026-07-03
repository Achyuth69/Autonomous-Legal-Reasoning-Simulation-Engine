import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.multi_model_debate_agent import MultiModelDebateAgent


@pytest.mark.asyncio
async def test_debate_agent_skipped_without_api_key():
    """Test that debate returns skipped status when Groq key is not configured"""
    agent = MultiModelDebateAgent()
    
    # Ensure it handles missing API key gracefully
    agent.client = None  # Simulate unconfigured Groq client
    
    result = await agent.execute({
        "facts": ["Fact 1"],
        "legal_issues": ["Issue 1"],
        "statutes": [],
        "precedents": [],
        "plaintiff_arguments": {},
        "defendant_arguments": {},
        "judgment": {},
        "parties": {}
    })
    
    assert result["status"] == "skipped"
    assert "error" in result
    assert "Groq" in result["error"]


@pytest.mark.asyncio
async def test_debate_agent_case_summary():
    """Test that case summary is properly prepared"""
    agent = MultiModelDebateAgent()
    
    summary = agent._prepare_case_summary(
        facts=["Plaintiff slipped on wet floor", "No warning signs were present"],
        legal_issues=["Negligence", "Premises liability"],
        statutes=[{"statute_name": "Negligence Act", "citation": "42 U.S.C. § 100"}],
        precedents=[{"case_name": "Smith v. Jones", "year": 2020}],
        plaintiff_args={"opening_statement": "Plaintiff suffered injuries", "main_arguments": [{"title": "Negligence"}]},
        defendant_args={"opening_statement": "Defendant denies liability", "substantive_defenses": [{"title": "Comparative fault"}]},
        judgment={"final_decision": {"verdict": "For Plaintiff"}},
        parties={"plaintiff": "John Doe", "defendant": "ABC Corp"}
    )
    
    assert "John Doe" in summary
    assert "ABC Corp" in summary
    assert "Negligence" in summary
    assert "Premises liability" in summary
    assert "Smith v. Jones" in summary


@pytest.mark.asyncio
async def test_debate_agent_model_name_mapping():
    """Test model name friendly mapping"""
    agent = MultiModelDebateAgent()
    
    assert agent._get_model_name("llama3-70b-8192") == "Llama 3 70B"
    assert agent._get_model_name("mixtral-8x7b-32768") == "Mixtral 8x7B"
    assert agent._get_model_name("gemma2-9b-it") == "Gemma 2 9B"
    assert agent._get_model_name("unknown-model") == "unknown-model"


@pytest.mark.asyncio
async def test_debate_context_building():
    """Test debate context built correctly from prior rounds"""
    agent = MultiModelDebateAgent()
    
    # Round 1 - no prior context
    context_r1 = agent._build_debate_context([], current_round=1)
    assert "first round" in context_r1.lower()
    
    # Round 2 - should reference round 1
    mock_transcript = [
        {"model": "Llama 3 70B", "round": 1, "argument": "My initial analysis is..."}
    ]
    context_r2 = agent._build_debate_context(mock_transcript, current_round=2)
    assert "Llama 3 70B" in context_r2
    assert "Round 2" in context_r2


@pytest.mark.asyncio
async def test_full_debate_with_mock_groq():
    """Test full debate flow with mocked Groq client"""
    agent = MultiModelDebateAgent()
    agent.client = MagicMock()
    agent.models = ["llama3-70b-8192", "mixtral-8x7b-32768"]
    agent.debate_rounds = 2
    
    # Mock Groq response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "This is a test legal argument."
    agent.client.chat.completions.create.return_value = mock_completion
    
    result = await agent.execute({
        "facts": ["Test fact"],
        "legal_issues": ["Test issue"],
        "statutes": [],
        "precedents": [],
        "plaintiff_arguments": {},
        "defendant_arguments": {},
        "judgment": {},
        "parties": {"plaintiff": "Plaintiff", "defendant": "Defendant"}
    })
    
    assert result["status"] == "success"
    assert "debate_transcript" in result
    assert len(result["debate_transcript"]) > 0
    assert "final_consensus" in result
