"""Tests for the router agent."""

import pytest
from unittest.mock import MagicMock, patch
from src.agents.router import router_node, route_query

@pytest.fixture
def mock_router_llm():
    with patch("src.agents.router.get_router_llm") as mock:
        yield mock

def test_router_classification_weather(mock_router_llm):
    """Test router classifies weather queries correctly."""
    # Mock LLM response
    mock_result = MagicMock()
    mock_result.intent = "weather"
    mock_result.weather_query = "Mumbai"
    mock_result.rag_query = None
    
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    mock_router_llm.return_value = mock_chain
    
    state = {"query": "What's the weather in Mumbai?"}
    result = router_node(state)
    
    assert result["query_type"] == "weather"
    assert result["weather_query"] == "Mumbai"

def test_router_classification_rag(mock_router_llm):
    """Test router classifies RAG queries correctly."""
    mock_result = MagicMock()
    mock_result.intent = "rag"
    mock_result.weather_query = None
    mock_result.rag_query = "What is RAG?"
    
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    mock_router_llm.return_value = mock_chain
    
    state = {"query": "What is RAG?"}
    result = router_node(state)
    
    assert result["query_type"] == "rag"
    assert result["rag_query"] == "What is RAG?"

def test_route_query_logic():
    """Test routing logic based on state."""
    assert route_query({"query_type": "weather"}) == "weather_agent"
    assert route_query({"query_type": "rag"}) == "rag_agent"
    assert route_query({"query_type": "both"}) == "both_agents"
    assert route_query({"query_type": "general"}) == "general_agent"
