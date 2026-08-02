"""
RAG Document Assistant — Health Check Route
"""

from fastapi import APIRouter
from app.config import settings
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is running and return configuration info."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        llm_provider=settings.llm_provider,
        vector_store="pinecone",
    )
