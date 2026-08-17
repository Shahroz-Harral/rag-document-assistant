import os
import tempfile
import pathlib
from fastapi import HTTPException
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB max size limit


def process_document_sync(file_bytes: bytes, filename: str, content_type: str) -> list[Document]:
    """
    Synchronously parses and chunks document bytes.
    Designed to run safely inside a worker thread via threadpool.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    file_ext = pathlib.Path(filename).suffix.lower()
    if content_type == "application/pdf" or file_ext == ".pdf":
        suffix = ".pdf"
    elif content_type == "text/plain" or file_ext == ".txt":
        suffix = ".txt"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}'. Supported formats: PDF, TXT."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(temp_path)
        else:
            loader = TextLoader(temp_path, encoding="utf-8")

        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)

        safe_filename = pathlib.Path(filename).name
        for i, chunk in enumerate(chunks):
            chunk.metadata["source"] = safe_filename
            chunk.metadata["chunk_index"] = i

        return chunks

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

