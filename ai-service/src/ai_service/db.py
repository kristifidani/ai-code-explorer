# --- Handle ChromaDB NumPy compatibility ---
# ChromaDB may fail with newer NumPy versions >2.0 that removed np.float_
# This ensures backward compatibility by aliasing float_ to float64
import hashlib
import numpy as np
from ai_service import constants, utils, errors

if not hasattr(np, "float_"):
    np.float_ = np.float64


import chromadb

# Set up ChromaDB client and persistent collection
chroma_path = utils.get_env_var(constants.CHROMA_STORE_PATH)
client = chromadb.PersistentClient(path=chroma_path)
collection = client.get_or_create_collection("code_chunks")


def _chunk_hash(chunk: str) -> str:
    """Returns a SHA256 hash for a code chunk."""
    return hashlib.sha256(chunk.encode("utf-8")).hexdigest()


def add_chunks(chunks: list[str], embeddings: list[list[float]]) -> None:
    """
    Add new code chunks and their embeddings to ChromaDB.

    Args:
        chunks: Code or text chunks to store.
        embeddings: Corresponding vector embeddings.

    Raises:
        DatabaseError: If database operation fails.
    """

    try:
        # Compute hashes for all chunks
        ids = [_chunk_hash(chunk) for chunk in chunks]

        # Check which IDs already exist
        existing = set()
        if ids:
            peek = collection.peek()
            if "ids" in peek:
                existing = set(peek["ids"])

        # Filter out chunks that already exist
        new_chunks = []
        new_embeddings = []
        new_ids = []
        for chunk, embedding, id_ in zip(chunks, embeddings, ids):
            if id_ not in existing:
                new_chunks.append(chunk)
                new_embeddings.append(embedding)
                new_ids.append(id_)

        if new_chunks:
            collection.add(
                documents=new_chunks,
                embeddings=new_embeddings,
                ids=new_ids,
            )
    except Exception as e:
        raise errors.DatabaseError.add_chunks_failed(e) from e


def query_chunks(text_embedding: list[float], number_of_results: int = 5) -> dict:
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
    if text_embedding is None or len(text_embedding) == 0:
        raise errors.InvalidParam.empty_embedding()
    if (
        not isinstance(number_of_results, int)
        or number_of_results < 1
        or number_of_results > 100
    ):
        raise errors.InvalidParam.invalid_results_count()

    try:
        return collection.query(
            query_embeddings=[text_embedding],
            n_results=number_of_results,
        )
    except Exception as e:
        raise errors.DatabaseError.query_chunks_failed(e) from e
