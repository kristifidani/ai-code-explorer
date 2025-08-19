"""
Embeddings Layer - Code and Text Semantic Embedding System.

This module provides high-level embedding functionality for converting code and natural
language into semantic vector representations. It uses specialized transformer models
optimized for code understanding and supports efficient batch processing.

Main Functions:
- embed_documents: Convert code/text documents into embeddings
- embed_query: Convert user queries into embeddings
- get_model: Access the underlying transformer model

See README.md for detailed information about the embedding model and architecture.
"""

from .encoding import embed_documents, embed_query
from .transformer import get_model

__all__ = [
    "embed_documents",
    "embed_query",
    "get_model",
]
