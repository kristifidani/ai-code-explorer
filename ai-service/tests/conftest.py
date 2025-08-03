from typing import Generator
import pytest
import chromadb

# ruff: noqa: E402
from dotenv import load_dotenv

load_dotenv()
from ai_service import db, constants, utils


def create_db_test_collection(collection_name: str) -> chromadb.Collection:
    chroma_path = utils.get_env_var(constants.CHROMA_STORE_PATH)
    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_or_create_collection(collection_name)


@pytest.fixture(scope="module")
def db_test_collection(request: pytest.FixtureRequest) -> chromadb.Collection:
    module_name = getattr(request, "module", "__name__")
    collection_name: str = f"{module_name}"
    return create_db_test_collection(collection_name)


@pytest.fixture(autouse=True)
def patch_and_clean_db_collection(
    monkeypatch: pytest.MonkeyPatch, db_test_collection: chromadb.Collection
) -> Generator[None, None, None]:
    monkeypatch.setattr(db, "collection", db_test_collection)

    yield

    # Clean up after each test
    ids: chromadb.IDs = db_test_collection.peek()["ids"]
    if ids:
        db_test_collection.delete(ids=ids)
