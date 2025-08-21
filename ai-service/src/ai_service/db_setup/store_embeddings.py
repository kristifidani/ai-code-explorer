import hashlib
import numpy as np
from ai_service import errors
from ai_service.db_setup.setup import get_collection


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
