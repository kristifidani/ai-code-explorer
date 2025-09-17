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
    canonical_github_url: HttpUrl | None = None  # Optional for general chat


def answer_question(
    user_question: str,
    repo_url: str | None = None,
) -> str:
    """
    Answer a question with optional repository context.

    Args:
        user_question: The user's question
        repo_url: Optional GitHub repository URL for context-aware answers

    Returns:
        AI-generated answer
    """
    try:
        # Handle project-specific questions with RAG context
        if repo_url:
            set_repo_context(repo_url)
            query_embedding = embed_query(user_question)
            results = query_chunks(query_embedding)
            documents = results.get("documents", [[]])

            if not documents or not documents[0]:
                prompt = (
                    f"I'm analyzing the GitHub project on this repository: {repo_url}\n\n"
                    f"USER QUESTION related to the current project: {user_question}\n\n"
                    "SITUATION: No relevant code context was found in the embedded documents for this project.\n\n"
                    "Please:\n"
                    "1. Provide a general answer to the question based on your knowledge\n"
                    "2. Explain that I couldn't find specific code context for this project\n"
                    "3. Suggest the user try:\n"
                    "   - Re-uploading the project (the embeddings might be incomplete)\n"
                    "   - Asking about different aspects of the codebase\n"
                    "   - Being more specific about file names, functions, or features\n\n"
                    "Keep your response helpful and encouraging."
                )
                logger.info(
                    "User question about project %s: %s", repo_url, user_question
                )
                logger.info("No relevant code snippets found for project.")
            else:
                unique_snippets = list(dict.fromkeys(documents[0]))
                context = "\n---\n".join(unique_snippets)
                prompt = (
                    f"You are an expert software engineer analyzing the GitHub project on this repository: {repo_url}\n\n"
                    f"USER QUESTION related to this project: {user_question}\n\n"
                    "RELEVANT CODE CONTEXT found from the similarity search:\n"
                    "```\n"
                    f"{context}\n"
                    "```\n\n"
                    "ANALYSIS INSTRUCTIONS:\n"
                    "1. **Direct Answer**: Start with a clear, direct answer to the user's question\n"
                    "2. **Code Analysis**: Examine the provided code context thoroughly\n"
                    "3. **Implementation Details**: Explain HOW things work, not just WHAT they do\n"
                    "4. **File References**: When mentioning code, reference the most relevant files/functions when possible\n"
                    "5. **Architecture Insights**: Explain flows and how different parts connect and interact\n"
                    "6. **Patterns & Practices**: Identify design patterns used, best practices, or potential improvements\n"
                    "7. **Completeness Check**: If context seems insufficient, clearly state what's missing\n\n"
                    "RESPONSE FORMAT:\n"
                    "- Start with a direct, friendly, exicting, positive and encouraging answer\n"
                    "- Use clear sections/bullet points for complex explanations\n"
                    "- Include the most relevant code examples if neccessary\n"
                    "- Be thorough but structured\n"
                    "- Keep responses complete - finish all thoughts and code examples\n"
                    "- If you can't answer fully, explain exactly why\n\n"
                    "Remember: Base your analysis ONLY on the observable code and documentation provided above. Do not speculate beyond what you can see."
                )
                logger.info(
                    "User question about project %s: %s", repo_url, user_question
                )
                logger.info("Context length: %d characters", len(context))

        # Handle general questions without project context
        else:
            prompt = (
                f"You are an expert AI assistant helping with general questions.\n\n"
                f"USER QUESTION: {user_question}\n\n"
                "INSTRUCTIONS:\n"
                "1. **Provide a comprehensive, well-structured answer** using your knowledge\n"
                "2. **If programming/tech related**: Include practical examples, best practices, and actionable insights\n"
                "3. **Use clear structure**: Break complex topics into sections or bullet points\n"
                "4. **Be thorough yet focused**: Cover the topic well without going off-tangent\n"
                "5. **Include context**: Explain not just 'what' but 'why' and 'when' it matters\n\n"
                "ADDITIONAL CONTEXT:\n"
                "- The user is using an AI Code Explorer tool which allows you to upload a github project through its url and ask questions about it.\n"
                "- If relevant, mention they can upload GitHub projects for code-specific analysis\n"
                "- Focus on being genuinely helpful and educational\n\n"
                "Provide your response in a clear, professional manner."
            )
            logger.info("General user question: %s", user_question)

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
    """
    Answer endpoint supporting both general and project-specific questions.

    - If canonical_github_url is provided: project-specific answer with RAG context
    - If canonical_github_url is None: general answer using LLM knowledge
    """
    repo_url = (
        str(request.canonical_github_url) if request.canonical_github_url else None
    )
    answer = answer_question(request.user_question, repo_url)
    return JSONResponse(status_code=200, content={"answer": answer})
