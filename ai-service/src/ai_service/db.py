# --- Handle ChromaDB NumPy compatibility ---
# ChromaDB may fail with newer NumPy versions >2.0 that removed np.float_
# This ensures backward compatibility by aliasing float_ to float64
import hashlib
import numpy as np
from ai_service import constants, utils, errors

if not hasattr(np, "float_"):
    np.float_ = np.float64  # type: ignore

import chromadb
from contextvars import ContextVar

# Set up ChromaDB client and persistent collection
chroma_path = utils.get_env_var(constants.CHROMA_STORE_PATH)
client = chromadb.PersistentClient(path=chroma_path)

_current_repo_url: ContextVar[str] = ContextVar("current_repo_url")


def set_repo_context(repo_url: str) -> None:
    """Set the current repository URL context for all DB operations."""
    _current_repo_url.set(repo_url)


def get_collection() -> chromadb.Collection:
    """Get or create a ChromaDB collection using the current repo context."""
    try:
        repo_url = _current_repo_url.get()
    except LookupError:
        raise errors.DatabaseError.no_repo_context()

    url_hash = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:12]
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    collection_name = f"{repo_name}_{url_hash}"
    return client.get_or_create_collection(collection_name)


def _chunk_hash(chunk: str) -> str:
    """Returns a SHA256 hash for a code chunk."""
    return hashlib.sha256(chunk.encode("utf-8")).hexdigest()


def add_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    """
    Add new code chunks and their embeddings to ChromaDB.

    Args:
        chunks: Code or text chunks to store.
        embeddings: Corresponding vector embeddings.

    Raises:
        DatabaseError: If database operation fails.
        InvalidParam: If chunks and embeddings counts don't match.
    """
    if len(chunks) != len(embeddings):
        raise errors.InvalidParam.embeddings_count_mismatch()

    collection = get_collection()
    try:
        # Compute hashes for all chunks
        ids = [_chunk_hash(chunk) for chunk in chunks]

        # Check which IDs already exist
        existing: set[str] = set()
        if ids:
            get_result = collection.get(ids=ids)
            if "ids" in get_result:
                existing = set(get_result["ids"])

        # Filter out chunks that already exist
        new_chunks: list[str] = []
        new_embeddings: list[list[float]] = []
        new_ids: list[str] = []
        for chunk, embedding, id_ in zip(chunks, embeddings, ids):
            if id_ not in existing:
                new_chunks.append(chunk)
                new_embeddings.append(embedding)
                new_ids.append(id_)

        if new_chunks:
            collection.add(
                documents=new_chunks,
                embeddings=np.array(new_embeddings, dtype=np.float32),
                ids=new_ids,
            )
    except Exception as e:
        raise errors.DatabaseError.add_chunks_failed(e) from e


def query_chunks(
    text_embedding: list[float],
    number_of_results: int = 3,
) -> chromadb.QueryResult:
    """
    Query ChromaDB for most similar documents.

    Args:
        text_embedding: Vector embedding of a user query.
        number_of_results: Number of results to return (1-100).

    Returns:
        Dict containing 'documents', 'distances', 'metadatas', and 'ids'.

    Raises:
        DatabaseError: If the query fails.
        InvalidParam: If parameters are invalid.
    """
    if len(text_embedding) == 0:
        raise errors.InvalidParam.empty_embedding()
    if number_of_results < 1 or number_of_results > 100:
        raise errors.InvalidParam.invalid_results_count()

    collection = get_collection()
    try:
        return collection.query(
            query_embeddings=[text_embedding],
            n_results=number_of_results,
        )
    except Exception as e:
        raise errors.DatabaseError.query_chunks_failed(e) from e
