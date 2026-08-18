"""
RAG Document Assistant — LLM Provider Setup (Model-Agnostic)

Switch between free LLM providers based on LLM_PROVIDER env var.
"""

import logging
from app.config import settings

logger = logging.getLogger(__name__)


def get_llm():
    """
    Factory function returning the configured LLM provider (Gemini or Groq)
    with automatic fallback between providers.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq

    models_to_try = []

    if settings.google_api_key:
        try:
            models_to_try.append(
                ChatGoogleGenerativeAI(
                    model="gemini-3.6-flash",
                    google_api_key=settings.google_api_key,
                    temperature=0.3,
                )
            )
        except Exception as e:
            logger.warning(f"Failed to load gemini-3.6-flash: {e}")

    if settings.groq_api_key:
        try:
            models_to_try.append(
                ChatGroq(
                    model="llama-3.1-8b-instant",
                    api_key=settings.groq_api_key,
                    temperature=0.3,
                )
            )
        except Exception as e:
            logger.warning(f"Failed to load llama-3.1-8b-instant: {e}")

    if not models_to_try:
        return ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=settings.google_api_key,
            temperature=0.3,
        )

    primary = models_to_try[0]
    fallbacks = models_to_try[1:]

    return primary.with_fallbacks(fallbacks) if fallbacks else primary
