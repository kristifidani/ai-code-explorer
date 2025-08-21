"""
Configuration for embeddings unit tests.
Initializes the embedding model so tests can run.
"""

import pytest
from unittest.mock import patch
import os


@pytest.fixture(scope="session", autouse=True)
def setup_embedding_model():
    """Initialize the embedding model for all tests in this module."""
    # Mock environment variables first
    with patch.dict(
        os.environ,
        {
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",  # Small, fast model for tests
        },
    ):
        # Import and initialize the model
        from ai_service.embeddings import initialize_model

        initialize_model()
        yield
