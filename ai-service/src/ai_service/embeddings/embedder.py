import logging
from functools import lru_cache
from typing import cast
from sentence_transformers import SentenceTransformer
from ai_service import errors, utils, constants
import torch


logger = logging.getLogger(__name__)


def _get_device() -> str:
    """
    Auto-detect the best available device for embedding computation.

    Returns:
        Device string: 'cuda', 'mps', or 'cpu'
    """

    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """
    Singleton accessor; loads the embedding model on first call only.
    Implements safe optimizations for code understanding tasks.

    Returns:
        Loaded SentenceTransformer model optimized for code embeddings.

    Raises:
        EmbeddingError: If model loading fails.
    """
    model_name = utils.get_env_var(constants.EMBEDDING_MODEL)
    device = _get_device()

    try:
        logger.info(f"Loading embedding model: {model_name}")
        logger.info(f"Device: {device}")

        return SentenceTransformer(
            model_name_or_path=model_name,
            device=device,
            trust_remote_code=False,  # Might be required for some code models
            cache_folder=None,  # Use default cache location
        )
    except Exception as e:
        raise errors.EmbeddingError.model_load_failed(model_name, e) from e


def _encode_texts(
    texts: list[str],
    *,
    is_query: bool = False,
    batch_size: int = 32,
    show_progress_bar: bool = False,
) -> list[list[float]]:
    """
    Internal function to create embeddings for a list of texts.
    Uses appropriate encoding methods based on context (query vs document).

    Args:
        texts: A list of strings to embed.
        is_query: Whether these are search queries (True) or documents (False).
        batch_size: Batch size for processing (default: 32).
        show_progress_bar: Show progress bar. (default: True)

    Returns:
        A list of embeddings (each embedding is a list of floats).

    Raises:
        EmbeddingError: If list of texts is empty, contains only empty strings, or encoding fails.
    """
    if not texts or all(not text.strip() for text in texts):
        raise errors.EmbeddingError.empty_input()
    model: SentenceTransformer = _get_model()

    try:
        # Use appropriate encoding method based on context
        if is_query and hasattr(model, "encode_query"):
            logger.debug(f"Encoding {len(texts)} queries using encode_query")
            embeddings = model.encode_query(  # type: ignore
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=batch_size,
                precision="float32",
                show_progress_bar=show_progress_bar,
                device=None,  # Use model's configured device
            )
        elif not is_query and hasattr(model, "encode_document"):
            logger.debug(f"Encoding {len(texts)} documents using encode_document")
            embeddings = model.encode_document(  # type: ignore
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=batch_size,
                precision="float32",
                show_progress_bar=show_progress_bar,
                device=None,  # Use model's configured device
            )
        return cast(list[list[float]], embeddings.tolist())  # type: ignore

    except Exception as e:
        raise errors.EmbeddingError(f"Failed to encode texts: {e}") from e


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Create embeddings for document texts (used during ingestion).

    Args:
        texts: A list of code/document strings to embed.

    Returns:
        A list of embeddings (each embedding is a list of floats).
    """
    return _encode_texts(texts, is_query=False)


def embed_query(text: str) -> list[float]:
    """
    Create an embedding for a search query text.

    Args:
        text: A search query string to embed.

    Returns:
        A list of floats representing the query embedding.
    """

    return _encode_texts([text], is_query=True)[0]
