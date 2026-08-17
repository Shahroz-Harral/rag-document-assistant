"""
RAG Document Assistant — LLM Provider Setup (Model-Agnostic)

Switch between free LLM providers by changing the LLM_PROVIDER env var.
LangChain's abstraction means your chains/agents don't need to change.
"""

from langchain_core.language_models import BaseChatModel
from app.config import settings


def get_llm():
    """
    Factory function that returns the Groq LLM with a Google Gemini fallback.

    If Groq fails (e.g., rate limits or downtime), LangChain automatically 
    routes the request to Gemini without crashing the application.
    """
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI

    groq_llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.groq_api_key,
        temperature=0.3,
    )

    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.google_api_key,
        temperature=0.3,
        convert_system_message_to_human=True,
    )

    # LangChain fallback magic
    return groq_llm.with_fallbacks([gemini_llm])
