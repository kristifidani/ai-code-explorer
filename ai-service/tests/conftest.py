from typing import Generator
import pytest
import chromadb

# ruff: noqa: E402
from dotenv import load_dotenv

load_dotenv()
from ai_service import constants, utils, db


def create_db_test_collection(collection_name: str) -> chromadb.Collection:
    chroma_path = utils.get_env_var(constants.CHROMA_STORE_PATH)
    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_or_create_collection(collection_name)


@pytest.fixture(scope="module")
def db_test_collection(request: pytest.FixtureRequest) -> chromadb.Collection:
    module = getattr(request, "module")
    module_name = getattr(module, "__name__")
    collection_name: str = f"{module_name}"
    return create_db_test_collection(collection_name)


@pytest.fixture(autouse=True)
def setup_test_context_and_clean_db(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    db_test_collection: chromadb.Collection,
) -> Generator[None, None, None]:
    # Create a fake repo URL based on the test module name
    module = getattr(request, "module")
    module_name = getattr(module, "__name__")
    test_repo_url = f"https://github.com/test/{module_name.replace('.', '-')}.git"

    # Set the repo context for this test module
    db.set_repo_context(test_repo_url)

    # Patch get_collection to return our test collection
    monkeypatch.setattr("ai_service.db.get_collection", lambda: db_test_collection)

    yield

    # Clean up after each test
    ids = db_test_collection.peek()["ids"]
    if ids:
        db_test_collection.delete(ids=ids)
