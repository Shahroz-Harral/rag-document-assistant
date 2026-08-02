"""
RAG Document Assistant — FastAPI Application

Entry point for the application. Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import chat, documents, health


app = FastAPI(
    title="RAG Document Assistant",
    description="Upload documents and ask questions — with guardrails for hallucination prevention.",
    version="0.1.0",
)

# CORS middleware (allow all origins in dev, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {
        "message": "RAG Document Assistant API",
        "docs": "/docs",
        "health": "/api/health",
    }
