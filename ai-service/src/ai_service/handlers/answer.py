import logging
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter

from ai_service import (
    db,
    embedder,
    ollama_client,
    errors,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class AnswerRequest(BaseModel):
    user_question: str
    canonical_github_url: HttpUrl


def answer_question(
    user_question: str,
    repo_url: str,
) -> str:
    try:
        db.set_repo_context(repo_url)
        question_embedding = embedder.embed_query(user_question)
        results = db.query_chunks(
            question_embedding,
        )
        documents = results.get("documents", [[]])

        if not documents or not documents[0]:
            prompt = (
                f"User question:\n{user_question}\n\n"
                "No relevant code context found. Please answer using your general knowledge."
            )
            logger.info("User question: %s", user_question)
            logger.info("No relevant code snippets found.")
        else:
            unique_snippets = list(dict.fromkeys(documents[0]))
            context = "\n---\n".join(unique_snippets)
            prompt = (
                "You are an AI assistant helping with a software project.\n\n"
                "Here is some relevant context from the uploaded project:\n"
                f"{context}\n\n"
                "User question:\n"
                f"{user_question}\n\n"
                "Answer in detail using the project as context. If context isn't relevant, fall back to general reasoning."
            )
            logger.info("User question: %s", user_question)
            logger.info("Most relevant code snippet(s): %s", context)

        answer = ollama_client.chat_with_ollama(prompt)
        logger.info("LLM answer: %s", answer)
    except errors.AIServiceError:
        logger.exception("Answer error")
        raise
    else:
        return answer


# Endpoint to answer a question
@router.post("/answer")
def answer_endpoint(request: AnswerRequest) -> JSONResponse:
    answer = answer_question(
        request.user_question,
        str(request.canonical_github_url),
    )
    return JSONResponse(status_code=200, content={"answer": answer})
