"""Tests for the weather agent."""

import pytest
from unittest.mock import MagicMock, patch

from src.agents.weather_agent import weather_agent_node
from src.tools.weather_tool import get_weather


@pytest.fixture
def mock_weather_tool():
    with patch("src.agents.weather_agent.get_weather") as mock:
        yield mock


@pytest.fixture
def mock_llm():
    with patch("src.agents.weather_agent.get_llm") as mock:
        yield mock


def test_weather_agent_success(mock_weather_tool, mock_llm):
    """Test weather agent happy path."""
    # Mock LLM city extraction
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value.content = "Mumbai"
    mock_llm.return_value = mock_llm_instance

    # Mock weather tool response
    # Since agent calls ainvoke inside asyncio.run, we Mock ainvoke
    # But get_weather is the tool function decorated with @tool?
    # Usually simplest is to patch invoking it.

    async def mock_ainvoke(*args, **kwargs):
        return "Sunny, 25C"

    mock_weather_tool.ainvoke = MagicMock(side_effect=mock_ainvoke)

    state = {
        "query": "Weather in Mumbai",
        "weather_query": "Mumbai",
        "messages": [],
    }

    result = weather_agent_node(state)

    assert result["weather_result"] == "Sunny, 25C"
    assert len(result["messages"]) == 1
    assert "Mumbai" in result["messages"][0]["content"]


def test_weather_tool_missing_api_key_returns_helpful_error():
    """Weather tool should fail gracefully when the API key is missing."""
    with patch("src.config.get_settings") as mock_get_settings:
        mock_get_settings.return_value = type(
            "Settings",
            (),
            {"openweathermap_api_key": ""},
        )()

        result = __import__("asyncio").run(get_weather.ainvoke({"city": "Mumbai"}))

    assert "OPENWEATHERMAP_API_KEY" in result
    assert "not configured" in result.lower()


def test_weather_agent_no_city():
    """Test fallback when no city extracted (though router usually handles this)."""
    # If implementation depends on LLM extraction within node vs passed from router
    # Current implementation uses state.get("weather_query") or extracts it
    pass
