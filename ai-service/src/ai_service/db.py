# --- Handle ChromaDB NumPy compatibility ---
# ChromaDB may fail with newer NumPy versions >2.0 that removed np.float_
# This ensures backward compatibility by aliasing float_ to float64
import numpy as np

if not hasattr(np, "float_"):
    np.float_ = np.float64

import uuid
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

# Set up ChromaDB client and persistent collection
chroma_path = os.getenv("CHROMA_STORE_PATH")
if not chroma_path:
    raise ValueError("CHROMA_STORE_PATH environment variable is required")

client = chromadb.PersistentClient(path=chroma_path)
collection = client.get_or_create_collection("code_chunks")


def add_chunks(chunks: list[str], embeddings: list[list[float]]) -> None:
    """
    Add new code chunks and their embeddings to ChromaDB.

    Args:
        chunks: Code or text chunks to store.
        embeddings: Corresponding vector embeddings.

    Raises:
        Exception: If database operation fails.
    """

    try:
        ids = [f"chunk-{uuid.uuid4()}" for _ in range(len(chunks))]
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
        )
    except Exception as e:
        raise Exception(f"Failed to add chunks to database: {e}") from e
