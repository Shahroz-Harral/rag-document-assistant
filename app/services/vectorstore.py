import logging
import datetime
from typing import Optional, Dict, Any, List
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

from app.config import settings
from app.core.embeddings import get_embeddings

logger = logging.getLogger(__name__)

_vectorstore_instance: Optional[PineconeVectorStore] = None
_indexed_documents_registry: Dict[str, Dict[str, Any]] = {}


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

    pc = Pinecone(api_key=settings.pinecone_api_key, pool_threads=1)
    index_name = settings.pinecone_index_name

    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        logger.warning(
            f"Pinecone index '{index_name}' does not exist in Pinecone account. "
            "Please ensure the index is created with dimension 3072 and metric 'cosine'."
        )

    try:
        embeddings = get_embeddings()
    except Exception as e:
        logger.error(f"Failed to initialize embeddings: {e}")
        return None

    try:
        _index = pc.Index(index_name)
        _vectorstore_instance = PineconeVectorStore(
            index=_index,
            embedding=embeddings,
        )
        logger.info(f"Initialized Pinecone VectorStore for index: {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialize PineconeVectorStore: {e}")
        return None

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
    Adds document chunks to the Pinecone vector store in batches and updates index registry.
    """
    if not chunks:
        return 0

    vectorstore = get_vectorstore()
    total_chunks = len(chunks)

    if vectorstore is not None:
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            vectorstore.add_documents(batch, async_req=False)

    # Register document metadata
    first_chunk = chunks[0]
    filename = first_chunk.metadata.get("source", "uploaded_document")
    _indexed_documents_registry[filename] = {
        "filename": filename,
        "chunks": total_chunks,
        "uploaded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    return total_chunks


def get_indexed_documents() -> List[Dict[str, Any]]:
    """
    Returns a list of all currently tracked/indexed documents.
    """
    return list(_indexed_documents_registry.values())


def delete_document_from_store(filename: str) -> bool:
    """
    Deletes all vector embeddings associated with a given filename from Pinecone and removes registry entry.
    """
    vectorstore = get_vectorstore()

    if vectorstore is not None:
        try:
            # Delete vectors matching metadata source filter
            vectorstore.delete(filter={"source": filename}, async_req=False)
        except Exception as e:
            logger.warning(f"Error deleting vectors for '{filename}' from Pinecone: {e}")

    if filename in _indexed_documents_registry:
        del _indexed_documents_registry[filename]
        return True

    return True
