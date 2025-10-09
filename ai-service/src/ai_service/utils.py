import os
from typing import Final
from ai_service import errors

CHROMA_STORE_PATH: Final[str] = "CHROMA_STORE_PATH"
LLM_MODEL: Final[str] = "LLM_MODEL"
EMBEDDING_MODEL: Final[str] = "EMBEDDING_MODEL"
PORT: Final[str] = "PORT"
MAX_CONTEXT_LENGTH: Final[str] = "MAX_CONTEXT_LENGTH"


def get_env_var(name: str) -> str:
    """
    Retrieve an environment variable, raising error if missing.

    Args:
        name: Name of the environment variable.

    Returns:
        The value of the environment variable.

    Raises:
        NotFound: If the variable is missing.
    """
    value = os.getenv(name)
    if value is None:
        raise errors.NotFound.env_variable(name)
    return value


def is_development() -> bool:
    """Check if running in development environment."""
    return os.getenv("ENVIRONMENT", "production").lower() == "development"
