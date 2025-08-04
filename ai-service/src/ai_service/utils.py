import os
from ai_service import errors


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
