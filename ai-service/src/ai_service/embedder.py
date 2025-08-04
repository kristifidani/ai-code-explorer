from functools import lru_cache
from typing import cast
from sentence_transformers import SentenceTransformer
from ai_service import errors


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Singleton accessor; loads on first call only."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Create embeddings for a list of texts.

    Args:
        texts: A list of strings to embed.

    Returns:
        A list of embeddings (each embedding is a list of floats).

    Raises:
        EmbeddingError: If texts is empty or contains only empty strings.
    """
    if not texts or all(not text.strip() for text in texts):
        raise errors.EmbeddingError.empty_input()

    model: SentenceTransformer = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)  # type: ignore
    return cast(list[list[float]], embeddings.tolist())


def embed_text(text: str) -> list[float]:
    """
    Embed a single text input and return the embedding as a list of floats.

    Args:
        text: A string to embed.

    Returns:
        A list of floats representing the text embedding.

    Raises:
        EmbeddingError: If text is empty or whitespace-only.
    """
    if not text.strip():
        raise errors.EmbeddingError.empty_input()
    return embed_texts([text])[0]
