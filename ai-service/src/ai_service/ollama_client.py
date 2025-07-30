from ai_service import utils, errors, constants
import ollama


def chat_with_ollama(prompt: str) -> str:
    """
    Query Ollama with a prompt and get a response.

    Args:
        prompt: Full prompt to send (including context).
        model: The local Ollama model to use.

    Returns:
        Model-generated response text.

    Raises:
        LLMQueryError: If the Ollama query fails for any reason.
    """
    model = utils.get_env_var(constants.LLM_MODEL)
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except (ollama.ResponseError, ConnectionError, KeyError) as e:
        raise errors.LLMQueryError.query_failed(e)
