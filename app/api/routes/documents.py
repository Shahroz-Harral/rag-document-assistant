"""
RAG Document Assistant — Document Upload & Listing Routes

Handles document upload, chunking, embedding, and listing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentUploadResponse, DocumentInfo

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or TXT) to be indexed for RAG.

    The document will be:
    1. Parsed and extracted
    2. Split into chunks
    3. Embedded and stored in Pinecone
    """
    # Validate file type
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not supported. Use PDF or TXT.",
        )

    # TODO: Implement document processing pipeline
    # 1. Read file content
    # 2. Split into chunks using LangChain text splitters
    # 3. Generate embeddings
    # 4. Upsert into Pinecone

    return DocumentUploadResponse(
        filename=file.filename or "unknown",
        chunks_created=0,
        message="Document upload endpoint ready — processing pipeline coming soon.",
    )


@router.get("/", response_model=list[DocumentInfo])
async def list_documents():
    """List all indexed documents."""
    # TODO: Query Pinecone for unique document sources
    return []
