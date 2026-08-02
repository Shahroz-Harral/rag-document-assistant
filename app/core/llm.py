"""
RAG Document Assistant — LLM Provider Setup (Model-Agnostic)

Switch between free LLM providers by changing the LLM_PROVIDER env var.
LangChain's abstraction means your chains/agents don't need to change.
"""

from langchain_core.language_models import BaseChatModel
from app.config import settings


def get_llm() -> BaseChatModel:
    """
    Factory function that returns the configured LLM provider.

    Supports:
        - gemini: Google Gemini via free AI Studio tier
        - groq: Groq for ultra-fast inference (free tier)

    Usage:
        llm = get_llm()
        response = llm.invoke("Hello!")
    """
    provider = settings.llm_provider.lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.google_api_key,
            temperature=0.3,
            convert_system_message_to_human=True,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            temperature=0.3,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            f"Set LLM_PROVIDER to 'gemini' or 'groq' in your .env file."
        )
