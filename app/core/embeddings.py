"""
RAG Document Assistant — Embedding Model Setup

Uses Google's embedding model (free with Gemini API key).
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Returns the embedding model for vectorizing documents and queries.

    Uses Google's text-embedding model (included in Gemini free tier).
    """
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.google_api_key,
    )
