import os
from ai_service import errors


def get_env_var(name: str, *, required: bool = True) -> str:
    """
    Retrieve an environment variable, optionally raising if missing.

    Args:
        name: Name of the environment variable.
        required: If True, raise NotFound if variable is missing.

    Returns:
        The value of the environment variable.

    Raises:
        NotFound: If required and variable is missing.
    """
    value = os.getenv(name)
    if required and value is None:
        raise errors.NotFound.env_variable(name)
    return value
