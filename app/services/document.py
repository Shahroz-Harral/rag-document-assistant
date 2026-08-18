"""
RAG Document Assistant — In-Memory Document Parser & Chunker

Parses PDF, TXT, MD, and text document bytes completely in-memory using pypdf and RecursiveCharacterTextSplitter.
Completely avoids temporary disk files, eliminating serverless filesystem errors.
"""

import io
import pathlib
from fastapi import HTTPException
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB max size limit

SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".log", ".json"}


def process_document_sync(file_bytes: bytes, filename: str, content_type: str) -> list[Document]:
    """
    Synchronously parses and chunks document bytes completely in-memory.
    Supports PDF, TXT, MD, CSV, LOG, and JSON files.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    file_ext = pathlib.Path(filename).suffix.lower()
    safe_filename = pathlib.Path(filename).name
    documents = []

    is_pdf = content_type == "application/pdf" or file_ext == ".pdf"
    is_text = (
        content_type.startswith("text/")
        or content_type in ["application/octet-stream", "text/plain", "text/markdown"]
        or file_ext in SUPPORTED_TEXT_EXTENSIONS
    )

    if is_pdf:
        try:
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            for page_idx, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    documents.append(
                        Document(
                            page_content=page_text,
                            metadata={"source": safe_filename, "page": page_idx + 1}
                        )
                    )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF document: {str(e)}")

    elif is_text:
        try:
            text_content = file_bytes.decode("utf-8", errors="ignore")
            if text_content.strip():
                documents.append(
                    Document(
                        page_content=text_content,
                        metadata={"source": safe_filename}
                    )
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse text document: {str(e)}")

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}' ({file_ext}). Supported formats: PDF, TXT, MD."
        )

    if not documents:
        raise HTTPException(status_code=400, detail="No readable text extracted from document.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = safe_filename
        chunk.metadata["chunk_index"] = i

    return chunks
