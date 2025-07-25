from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

from .exceptions import EmbeddingError


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Singleton accessor; loads on first call only."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Create embeddings for a list of texts.

    Args:
        texts: A list of strings to embed.

    Returns:
        A NumPy array of embeddings.

    Raises:
        EmbeddingError: If texts is empty or contains only empty strings.
    """
    if not texts or all(not text.strip() for text in texts):
        raise EmbeddingError("Cannot embed empty or whitespace-only texts")
    return _get_model().encode(texts, convert_to_numpy=True)


def embed_text(text: str) -> np.ndarray:
    """
    Embed a single text input and return the embedding as a NumPy array.

    Args:
        text: A string to embed.

    Returns:
        A NumPy array representing the text embedding.

    Raises:
        EmbeddingError: If text is empty or whitespace-only.
    """
    if not text.strip():
        raise EmbeddingError("Cannot embed empty or whitespace-only text")
    return embed_texts([text])[0]
