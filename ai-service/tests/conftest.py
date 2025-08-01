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
def db_test_collection(request) -> chromadb.Collection:
    collection_name = f"{request.module.__name__}"
    return create_db_test_collection(collection_name)


@pytest.fixture(autouse=True)
def patch_and_clean_db_collection(
    monkeypatch, db_test_collection
) -> Generator[None, None, None]:
    monkeypatch.setattr(db, "collection", db_test_collection)

    yield

    # Clean up after each test
    ids = db_test_collection.peek()["ids"]
    if ids:
        db_test_collection.delete(ids=ids)
