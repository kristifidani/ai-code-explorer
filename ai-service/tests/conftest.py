from typing import Generator
import pytest
import os
from unittest.mock import patch

from ai_service.db_setup import set_repo_context, initialize_db
from ai_service.embeddings import initialize_model


@pytest.fixture(scope="session", autouse=True)
def setup_services_for_integration_tests(
    tmp_path_factory: pytest.TempPathFactory,
):
    """Initialize both DB and embedding model for integration tests."""
    # Mock environment variables for tests
    chroma_dir = tmp_path_factory.mktemp("")
    with patch.dict(
        os.environ,
        {
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",  # Small model for tests
            "CHROMA_STORE_PATH": str(chroma_dir),
        },
    ):
        initialize_db()
        initialize_model()
        yield


@pytest.fixture(autouse=True)
def setup_test_context_and_clean_db(
    request: pytest.FixtureRequest,
) -> Generator[None, None, None]:
    # Create a fake repo URL based on the test module name
    module = getattr(request, "module")
    module_name = getattr(module, "__name__")
    test_repo_url = f"https://github.com/test/{module_name.replace('.', '-')}.git"

    # Set the repo context for this test module
    set_repo_context(test_repo_url)

    yield

    # Clean up after each test - use the real get_collection() function
    from ai_service.db_setup import get_collection

    try:
        collection = get_collection()
        ids = collection.peek()["ids"]
        if ids:
            collection.delete(ids=ids)
    except Exception:
        # If collection doesn't exist or other error, just continue
        pass
