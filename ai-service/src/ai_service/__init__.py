"""
AI Service - Code Understanding and Question Answering System.

This service provides intelligent code analysis and question answering capabilities
using embeddings and large language models. It can ingest GitHub repositories,
create semantic embeddings of code, and answer questions about the codebase.

Main Components:
- embeddings: Code and text embedding functionality
- db_setup: Database operations for storing and querying embeddings
- handlers: REST API endpoints for ingestion and answering
- ollama_client: Integration with Ollama LLM
- project_ingestor: GitHub repository processing

Core functionality is exposed through submodules for easy integration.
"""

from __future__ import annotations

# Core modules
from . import errors
from . import utils

# Submodules for external use
from . import embeddings
from . import db_setup
from . import handlers

__version__ = "1.0.0"


def __getattr__(name: str):
    """Lazy attribute access to avoid import side-effects.

    Importing `ai_service.main` at package import time breaks `python -m ai_service.main`
    by pre-loading the module (runpy emits a warning) and can create circular imports.
    """

    if name in {"app", "main"}:
        from . import main as _main

        return getattr(_main, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Core modules
    "errors",
    "utils",
    # Submodules
    "embeddings",
    "db_setup",
    "handlers",
    # Version
    "__version__",
]
