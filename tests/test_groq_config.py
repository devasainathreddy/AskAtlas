"""Tests for Groq configuration and error handling."""

import pytest
from unittest.mock import patch, MagicMock
from src.config import Settings, get_llm, get_groq_client, _validate_api_key
from app import format_api_error
import groq


def test_groq_default_settings():
    """Verify Groq is configured as default provider with supported model."""
    settings = Settings(GROQ_API_KEY="gsk_test123")
    assert settings.llm_provider == "groq"
    assert settings.llm_model == "llama-3.3-70b-versatile"
    assert settings.groq_api_key == "gsk_test123"


def test_groq_api_key_validation():
    """Verify validation raises clear ValueError when GROQ_API_KEY is missing or placeholder."""
    with pytest.raises(ValueError) as excinfo:
        _validate_api_key("groq", "")
    assert "Groq (GROQ_API_KEY) is not configured" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        _validate_api_key("groq", "your_groq_api_key_here")
    assert "Groq (GROQ_API_KEY) is not configured" in str(excinfo.value)


def test_get_llm_groq():
    """Verify get_llm returns ChatGroq when provider is groq."""
    with patch("src.config.get_settings") as mock_settings:
        mock_settings.return_value = Settings(
            LLM_PROVIDER="groq",
            LLM_MODEL="llama-3.3-70b-versatile",
            GROQ_API_KEY="gsk_valid_test_key_123",
        )
        llm = get_llm(temperature=0.2)
        assert llm.model_name == "llama-3.3-70b-versatile"
        assert llm.temperature == 0.2


def test_get_groq_client():
    """Verify get_groq_client returns official Groq SDK client."""
    with patch("src.config.get_settings") as mock_settings:
        mock_settings.return_value = Settings(
            LLM_PROVIDER="groq",
            GROQ_API_KEY="gsk_valid_test_key_123",
        )
        client = get_groq_client()
        assert isinstance(client, groq.Groq)
        assert client.api_key == "gsk_valid_test_key_123"


def test_format_api_error_handling():
    """Verify format_api_error properly categorizes auth, rate limit, and network errors."""
    req = MagicMock()

    # 1. Authentication Error
    auth_err = groq.AuthenticationError(
        message="Invalid API Key",
        response=MagicMock(status_code=401),
        body={"error": "unauthorized"},
    )
    msg = format_api_error(auth_err)
    assert "Authentication Error" in msg

    # 2. Rate Limit Error
    rate_err = groq.RateLimitError(
        message="Rate limit reached",
        response=MagicMock(status_code=429),
        body={"error": "rate_limit_exceeded"},
    )
    msg = format_api_error(rate_err)
    assert "Rate Limit" in msg

    # 3. Connection / Network Error
    net_err = groq.APIConnectionError(request=req)
    msg = format_api_error(net_err)
    assert "Network Error" in msg

    # 4. Timeout Error
    timeout_err = groq.APITimeoutError(request=req)
    msg = format_api_error(timeout_err)
    assert "Timeout" in msg
