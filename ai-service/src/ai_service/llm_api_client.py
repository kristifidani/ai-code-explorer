from functools import lru_cache
from ai_service import utils, errors
from openai import OpenAI


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    return OpenAI(api_key=utils.get_env_var(utils.OPENAI_API_KEY))


def chat_with_llm(prompt: str) -> str:
    """
    Query LLM with a prompt and get a response.
    """
    try:
        model = utils.get_env_var(utils.LLM_MODEL)
        client = _get_client()
        response = client.chat.completions.create(  # type: ignore
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.choices[0].message.content
        if content is None:
            raise errors.LLMQueryError.query_failed(
                ValueError("LLM returned empty content")
            )
        return content

    except Exception as e:
        # OpenAI raises different exception types; keep your abstraction clean
        raise errors.LLMQueryError.query_failed(e) from e
