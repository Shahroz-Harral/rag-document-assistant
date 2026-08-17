import logging
from typing import Optional
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

from app.config import settings
from app.core.embeddings import get_embeddings

logger = logging.getLogger(__name__)

_vectorstore_instance: Optional[PineconeVectorStore] = None


def init_vectorstore() -> PineconeVectorStore:
    """
    Initializes and returns the cached Pinecone vector store instance at app startup.
    """
    global _vectorstore_instance
    if _vectorstore_instance is not None:
        return _vectorstore_instance

    if not settings.pinecone_api_key:
        logger.warning("PINECONE_API_KEY is not set.")
        return None

    pc = Pinecone(api_key=settings.pinecone_api_key)
    index_name = settings.pinecone_index_name

    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        logger.warning(
            f"Pinecone index '{index_name}' does not exist in Pinecone account. "
            "Please ensure the index is created with dimension 3072 and metric 'cosine'."
        )

    embeddings = get_embeddings()
    _vectorstore_instance = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        pinecone_api_key=settings.pinecone_api_key,
    )
    logger.info(f"Initialized Pinecone VectorStore for index: {index_name}")
    return _vectorstore_instance


def get_vectorstore() -> PineconeVectorStore:
    """
    Returns the cached Pinecone vector store instance.
    """
    if _vectorstore_instance is None:
        return init_vectorstore()
    return _vectorstore_instance


def add_documents_to_store(chunks: list[Document], batch_size: int = 100) -> int:
    """
    Adds document chunks to the Pinecone vector store in batches.
    """
    if not chunks:
        return 0

    vectorstore = get_vectorstore()
    total_chunks = len(chunks)

    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        vectorstore.add_documents(batch)

    return total_chunks

