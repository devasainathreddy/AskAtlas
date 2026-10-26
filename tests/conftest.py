import pytest
import os
from unittest.mock import MagicMock
from src.config import Settings

@pytest.fixture
def mock_settings():
    """Mock environment settings"""
    return Settings(
        GROQ_API_KEY="gsk_test_groq_key",
        GOOGLE_API_KEY="test_key",
        OPENWEATHERMAP_API_KEY="test_weather_key",
        LLM_PROVIDER="groq",
        LLM_MODEL="llama-3.3-70b-versatile",
        QDRANT_URL="http://localhost:6333",
        QDRANT_COLLECTION_NAME="test_collection"
    )

@pytest.fixture(autouse=True)
def mock_env(monkeypatch, mock_settings):
    """Automatically mock env vars for all tests"""
    for key, value in mock_settings.model_dump().items():
        if isinstance(value, str):
            monkeypatch.setenv(key.upper(), value)
    return mock_settings
