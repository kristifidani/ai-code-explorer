from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

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
        A list of embeddings (lists of floats).
    """
    return _get_model().encode(texts, convert_to_numpy=True)

def embed_text(text: str) -> list[float]:
    """
    Embed a single text input as a NumPy array.
    """
    return embed_texts([text])[0]
