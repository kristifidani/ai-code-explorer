from .exceptions import LLMQueryError
import ollama


def chat_with_ollama(prompt: str, model: str = "gemma3") -> str:
    """
    Query Ollama with a prompt and get a response.

    Args:
        prompt: Full prompt to send (including context).
        model: The local Ollama model to use.

    Returns:
        Model-generated response text.

    Raises:
        ConnectionError: If unable to connect to Ollama service.
        KeyError: If the model is not available.
        ResponseError: If response is invalid.
    """

    try:
        response = ollama.chat(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except (ollama.ResponseError, ConnectionError, KeyError) as e:
        raise LLMQueryError(f"Ollama query failed: {e}") from e
