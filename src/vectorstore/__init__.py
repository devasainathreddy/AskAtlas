"""Vectorstore package for AskAtlas."""

from src.vectorstore.qdrant_client import (
    get_embeddings,
    get_qdrant_client,
    get_vector_store,
    get_retriever,
    add_documents,
)

__all__ = [
    "get_embeddings",
    "get_qdrant_client", 
    "get_vector_store",
    "get_retriever",
    "add_documents",
]
