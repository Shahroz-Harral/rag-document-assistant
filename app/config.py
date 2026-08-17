"""
RAG Document Assistant — Configuration

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # App
    app_env: str = Field(default="development")
    log_level: str = Field(default="info")
    allowed_origins: str = Field(default="*")

    # LLM Provider
    llm_provider: str = Field(default="gemini", description="Options: gemini, groq")
    google_api_key: str = Field(default="")
    groq_api_key: str = Field(default="")

    # Vector Database
    pinecone_api_key: str = Field(default="")
    pinecone_index_name: str = Field(default="rag-documents")

    # Observability
    langsmith_api_key: str = Field(default="")
    langsmith_project: str = Field(default="rag-document-assistant")
    langchain_tracing_v2: bool = Field(default=True)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()
