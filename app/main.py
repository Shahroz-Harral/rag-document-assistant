"""
RAG Document Assistant — FastAPI Application

Entry point for the application. Run with:
    uvicorn app.main:app --reload
"""

import os
import socket
import logging

# Patch socket.getaddrinfo to prefer IPv4.
# On macOS, Python's default socket resolution tries IPv6 first and hangs for 150s
# if the local network route for IPv6 drops packets, before falling back to IPv4.
_old_getaddrinfo = socket.getaddrinfo
def _allowed_gai_families(*args, **kwargs):
    responses = _old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = _allowed_gai_families

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.api.routes import chat, documents, health
from app.services.vectorstore import init_vectorstore

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes global resources on startup."""
    logger.info("Initializing vector store connection...")
    try:
        init_vectorstore()
    except Exception as e:
        logger.warning(f"Vector store initialization deferred: {e}")
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="RAG Document Assistant",
    description="Upload documents and ask questions — with guardrails for hallucination prevention.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration
origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
allow_credentials = False if "*" in origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# Mount static web frontend files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "RAG Document Assistant API",
            "docs": "/docs",
            "health": "/api/health",
        }
