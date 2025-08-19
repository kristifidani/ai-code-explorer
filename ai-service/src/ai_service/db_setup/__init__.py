"""
Database setup and operations for ChromaDB embeddings storage.

This module provides database configuration, storage, and query operations
for code embeddings using ChromaDB as the vector database backend.
"""

from .setup import set_repo_context, get_collection
from .store_embeddings import add_chunks
from .query_embeddings import query_chunks

__all__ = [
    "set_repo_context",
    "get_collection",
    "add_chunks",
    "query_chunks",
]
