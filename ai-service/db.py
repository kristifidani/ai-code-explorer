# --- Handle ChromaDB NumPy compatibility ---
import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64

import uuid
import chromadb

# Set up ChromaDB client and persistent collection
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection("code_chunks")

def add_chunks(chunks: list[str], embeddings: list[list[float]]):
    """
    Add new code chunks and their embeddings to ChromaDB.

    Args:
        chunks: Code or text chunks to store.
        embeddings: Corresponding vector embeddings.
        metadata: Optional info like filename, function name.

    Raises:
        Exception: If database operation fails.
    """

    try:
        ids = [f"chunk-{uuid.uuid4()}" for _ in range(len(chunks))]
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids
        )
    except Exception as e:
        raise Exception(f"Failed to add chunks to database: {e}") from e


