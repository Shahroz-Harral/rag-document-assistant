"""
RAG Document Assistant — Pydantic Schemas

Request and response models for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional


# --- Chat ---

class ChatRequest(BaseModel):
    """Request body for the /api/chat endpoint."""
    question: str = Field(..., min_length=1, max_length=2000, description="The question to ask about your documents")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of document chunks to retrieve")
    session_id: Optional[str] = Field(default=None, description="Optional session ID to maintain chat history")


class SourceChunk(BaseModel):
    """A source document chunk used to generate the answer."""
    content: str = Field(..., description="The text content of the chunk")
    source: str = Field(..., description="The source document filename")
    page: Optional[int] = Field(default=None, description="Page number if applicable")
    score: float = Field(..., description="Relevance score (0-1)")


class ChatResponse(BaseModel):
    """Response body for the /api/chat endpoint."""
    answer: str = Field(..., description="The generated answer")
    sources: list[SourceChunk] = Field(default_factory=list, description="Source chunks used")
    model: str = Field(..., description="The LLM model used")
    session_id: Optional[str] = Field(default=None, description="Session ID for multi-turn conversation")


# --- Documents ---

class DocumentUploadResponse(BaseModel):
    """Response after uploading and indexing a document."""
    filename: str
    chunks_created: int
    message: str


class DocumentInfo(BaseModel):
    """Information about an indexed document."""
    filename: str
    chunks: int
    uploaded_at: str


# --- Health ---

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "0.1.0"
    llm_provider: str
    vector_store: str = "pinecone"
