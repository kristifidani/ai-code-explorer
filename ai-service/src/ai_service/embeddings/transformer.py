import logging
from typing import Optional
from ai_service import errors, utils, constants
import torch
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)

# Global model variable - initialized once at startup
_model: Optional[SentenceTransformer] = None


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


def initialize_model(trust_remote_code: bool = False) -> None:
    """Initialize the embedding model at application startup."""
    global _model
    if _model is None:
        model_name = utils.get_env_var(constants.EMBEDDING_MODEL)
        device = _get_device()

        try:
            logger.info(f"Device: {device}")

            _model = SentenceTransformer(
                model_name_or_path=model_name,
                device=device,
                trust_remote_code=trust_remote_code,
                cache_folder=None,  # Use default cache location
            )
        except Exception as e:
            raise errors.EmbeddingError.model_load_failed(model_name, e) from e


def get_model() -> SentenceTransformer:
    """
    Get the initialized embedding model.

    Returns:
        Loaded SentenceTransformer model optimized for code embeddings.

    Raises:
        EmbeddingError: If model not initialized.
    """
    if _model is None:
        raise errors.EmbeddingError.missing_model()
    return _model
