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

# Core modules
from . import errors
from . import utils

# Main application
from .main import app, main

# Submodules for external use
from . import embeddings
from . import db_setup
from . import handlers

__version__ = "1.0.0"

__all__ = [
    # Core modules
    "errors",
    "utils",
    # Main app
    "app",
    "main",
    # Submodules
    "embeddings",
    "db_setup",
    "handlers",
    # Version
    "__version__",
]
