import logging
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter

from ai_service import (
    ollama_client,
    errors,
)
from ai_service.embeddings import embed_query
from ai_service.db_setup import set_repo_context, query_chunks

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
        set_repo_context(repo_url)
        query_embedding = embed_query(user_question)
        results = query_chunks(
            query_embedding,
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
                "You are an AI assistant analyzing a software project. Your goal is to provide helpful, accurate answers based on the code context.\n\n"
                "CONTEXT FROM PROJECT:\n"
                f"{context}\n\n"
                f"QUESTION: {user_question}\n\n"
                "INSTRUCTIONS:\n"
                "- Analyze the provided code context thoroughly\n"
                "- Answer based on what you can observe in the code, configurations, and documentation\n"
                "- If you find relevant implementation details, explain how things work\n"
                "- If you see file structures or directories, mention their organization\n"
                "- When discussing features, explain what exists vs what doesn't exist\n"
                "- Be specific about file locations when relevant\n"
                "- If the context doesn't contain enough information, say so clearly\n"
                "- Keep responses concise but informative\n\n"
                "ANSWER:"
            )
            logger.info("User question: %s", user_question)
            logger.info("Most relevant code snippet(s): %s", context)
            logger.info(f"Context length: {len(context)} characters")

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
