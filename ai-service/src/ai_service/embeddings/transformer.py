import logging
from functools import lru_cache
from ai_service import errors, utils, constants
import torch
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


def _get_device() -> str:
    """
    Auto-detect the best available device for embedding computation.

    Returns:
        Device string: 'cuda', 'mps', or 'cpu'
    """

    if torch.cuda.is_available():
        return "cuda"

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"

    return "cpu"


@lru_cache(maxsize=1)
def get_model(
    trust_remote_code: bool = False,  # Might be required for some code models
) -> SentenceTransformer:
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
            trust_remote_code=trust_remote_code,
            cache_folder=None,  # Use default cache location
        )
    except Exception as e:
        raise errors.EmbeddingError.model_load_failed(model_name, e) from e
