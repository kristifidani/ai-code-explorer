"""
Code chunking module for breaking down source files into meaningful segments.

This module provides different strategies for chunking code files to optimize
embedding storage and retrieval for semantic search.
"""

from .strategies import chunk_code_file

__all__ = ["chunk_code_file"]
