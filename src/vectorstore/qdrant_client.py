"""Qdrant vector store client and operations."""

import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.config import get_settings

# Model configuration
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIMENSION = 768  # all-mpnet-base-v2 produces 768-dim vectors

# Device detection with fallback
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def get_embeddings() -> HuggingFaceEmbeddings:
    """Get the embeddings model using sentence-transformers."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": DEVICE},
        encode_kwargs={"normalize_embeddings": True},
    )


def get_qdrant_client() -> QdrantClient:
    """Get the Qdrant client."""
    settings = get_settings()
    if settings.qdrant_api_key:
        return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection_exists() -> None:
    """Ensure the collection exists in Qdrant."""
    settings = get_settings()
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if settings.qdrant_collection_name not in collection_names:
            client.create_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE),
            )
            print(f"Created collection: {settings.qdrant_collection_name}")
    except Exception as e:
        print(f"Warning: Could not connect to Qdrant or initialize collection: {e}")


def get_vector_store() -> QdrantVectorStore:
    """Get the Qdrant vector store."""
    settings = get_settings()
    ensure_collection_exists()
    
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=settings.qdrant_collection_name,
        embedding=get_embeddings(),
    )


def get_retriever(k: int = 4):
    """Get a retriever for document search.
    
    Args:
        k: Number of documents to retrieve
        
    Returns:
        A retriever instance
    """
    vector_store = get_vector_store()
    return vector_store.as_retriever(search_kwargs={"k": k})


def add_documents(documents: list) -> None:
    """Add documents to the vector store.
    
    Args:
        documents: List of Document objects to add
    """
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    print(f"Added {len(documents)} documents to the vector store.")
