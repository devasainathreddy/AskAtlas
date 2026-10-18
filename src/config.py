"""Configuration settings for AskAtlas."""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    google_api_key: str = Field("", alias="GOOGLE_API_KEY")
    openweathermap_api_key: str = Field("", alias="OPENWEATHERMAP_API_KEY")

    # LangSmith
    langchain_tracing_v2: bool = Field(True, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field("", alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field("AskAtlas", alias="LANGCHAIN_PROJECT")

    # Qdrant
    qdrant_url: str = Field("http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(None, alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(
        "askatlas_documents", alias="QDRANT_COLLECTION_NAME"
    )

    # LLM Configuration
    llm_provider: Literal["openai", "google", "ollama"] = Field("google", alias="LLM_PROVIDER")
    llm_model: str = Field("gemini-3.8-flash", alias="LLM_MODEL")
    ollama_base_url: str = Field("http://localhost:11434", alias="OLLAMA_BASE_URL")

    # Application
    pdf_path: str = Field("data/rag.pdf", alias="PDF_PATH")


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_llm(temperature: float = 0.0, format: Optional[str] = None):
    """Get LLM based on configured provider.
    
    Args:
        temperature: Temperature for LLM responses
        format: Output format ('json' for JSON mode on Ollama)
        
    Returns:
        Configured LLM instance (OpenAI, Google, or Ollama)
    """
    settings = get_settings()
    
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        kwargs = {
            "model": settings.llm_model,
            "base_url": settings.ollama_base_url,
            "temperature": temperature,
        }
        if format:
            kwargs["format"] = format
        return ChatOllama(**kwargs)
    elif settings.llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=temperature,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            temperature=temperature,
        )


def get_llm_with_structured_output(schema: type[BaseModel], temperature: float = 0.0):
    """Get LLM configured for structured output (guaranteed schema response).
    
    Use for: Query classification, data extraction, etc.
    The model ALWAYS returns data in the specified schema.
    
    Args:
        schema: Pydantic model for structured output
        temperature: Temperature for LLM responses
    """
    settings = get_settings()
    
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )
        return llm.with_structured_output(schema)
    elif settings.llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=temperature,
        )
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            temperature=temperature,
        )
    return llm.with_structured_output(schema)


def get_llm_with_tools(tools: list, temperature: float = 0.0):
    """Get LLM with tools bound (model decides when to call).
    
    Use for: Agentic workflows where model chooses to call tools.
    
    Args:
        tools: List of tools to bind
        temperature: Temperature for LLM responses
    """
    llm = get_llm(temperature=temperature)
    return llm.bind_tools(tools)
