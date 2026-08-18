"""
RAG Document Assistant — Document Upload, Listing, and Deletion Routes

Handles document upload, chunking, embedding, listing, and deletion.
"""

import anyio
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentUploadResponse, DocumentInfo
from app.services.document import process_document_sync
from app.services.vectorstore import (
    add_documents_to_store,
    get_indexed_documents,
    delete_document_from_store,
)

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or TXT) to be indexed for RAG.

    The document will be:
    1. Read safely from payload
    2. Parsed & chunked in threadpool
    3. Embedded and stored in Pinecone in threadpool
    """
    filename = file.filename or "uploaded_document"
    content_type = file.content_type or ""

    file_bytes = await file.read()

    # Offload blocking parsing & text splitting to worker thread pool
    chunks = await anyio.to_thread.run_sync(
        process_document_sync, file_bytes, filename, content_type
    )

    # Offload blocking Pinecone vector store API calls to worker thread pool
    added_count = await anyio.to_thread.run_sync(
        add_documents_to_store, chunks
    )

    return DocumentUploadResponse(
        filename=filename,
        chunks_created=added_count,
        message="Document uploaded and indexed successfully.",
    )


@router.get("/", response_model=list[DocumentInfo])
async def list_documents():
    """List all currently indexed documents."""
    docs = get_indexed_documents()
    return [
        DocumentInfo(
            filename=d["filename"],
            chunks=d["chunks"],
            uploaded_at=d["uploaded_at"]
        )
        for d in docs
    ]


@router.delete("/{filename}")
async def delete_document(filename: str):
    """
    Delete a document and its vector embeddings from Pinecone.
    """
    success = await anyio.to_thread.run_sync(delete_document_from_store, filename)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found.")

    return {"message": f"Document '{filename}' deleted successfully.", "filename": filename}
