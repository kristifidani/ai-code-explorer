from ai_service import utils, errors
from openai import OpenAI


def chat_with_llm(prompt: str) -> str:
    """
    Query LLM with a prompt and get a response.
    """
    try:
        model = utils.get_env_var(utils.LLM_MODEL)
        client = OpenAI(api_key=utils.get_env_var(utils.OPENAI_API_KEY))  # type: ignore
        response = client.chat.completions.create(  # type: ignore
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content  # type: ignore

    except Exception as e:
        # OpenAI raises different exception types; keep your abstraction clean
        raise errors.LLMQueryError.query_failed(e) from e
