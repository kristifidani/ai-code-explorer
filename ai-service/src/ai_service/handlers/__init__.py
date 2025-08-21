"""
HTTP Handlers - REST API Endpoints for AI Service.

This module contains FastAPI router endpoints for the main AI service functionality:

Endpoints:
- POST /ingest: Ingest a GitHub repository and create embeddings.
- POST /answer: Answer questions about an ingested repository.
"""

from .ingest import router as ingest_router, ingest_github_project
from .answer import router as answer_router, answer_question

__all__ = [
    "ingest_router",
    "answer_router",
    "ingest_github_project",
    "answer_question",
]
