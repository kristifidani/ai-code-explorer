# ruff: noqa: E402


from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
from ai_service import (
    db,
    embedder,
    ollama_client,
    errors,
    project_ingestor,
    utils,
    constants,
)

# FastAPI imports
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI()


# Most elegant solution - FastAPI exception handlers
@app.exception_handler(errors.AIServiceError)
async def ai_service_error_handler(request: Request, exc: errors.AIServiceError):
    status_code = 404 if isinstance(exc, errors.NotFound) else 400
    logging.error(f"AIServiceError: {exc}")
    return JSONResponse(
        status_code=status_code,
        content={"error": str(exc), "code": exc.__class__.__name__},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.exception("Unexpected error")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": "InternalError"},
    )


def ingest_github_project(repo_url: str, collection_name: str) -> None:
    project_dir = project_ingestor.clone_github_repo(repo_url)
    try:
        logging.info("Scanning project directory ...")
        code_files = project_ingestor.scan_code_files(project_dir)
        logging.info(f"Found {len(code_files)} code files to process.")

        code_snippets: list[str] = []
        embeddings: list[list[float]] = []

        logging.info("Embedding content for each file ...")
        for file_path in code_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    code = f.read().strip()
                    if not code:
                        logging.warning(f"Skipping empty file: {file_path}")
                        continue
                    code_snippets.append(code)
                    embeddings.append(embedder.embed_text(code))
            except FileNotFoundError:
                err = errors.FileReadError.file_not_found(file_path)
                logging.error(err)
                continue
            except PermissionError:
                err = errors.FileReadError.permission_denied(file_path)
                logging.error(err)
                continue
            except UnicodeDecodeError:
                err = errors.FileReadError.decode_error(file_path)
                logging.error(err)
                continue
            except OSError as e:
                err = errors.FileReadError.os_error(file_path, e)
                logging.error(err)
                continue

        if code_snippets:
            db.add_chunks(code_snippets, embeddings, collection_name)
            logging.info(f"Stored {len(code_snippets)} code snippets in ChromaDB.")
        else:
            logging.warning("No valid code snippets found to store.")
    finally:
        logging.info("Cleaning up project directory ...")
        project_ingestor.cleanup_dir(project_dir)


# Request models for FastAPI
class IngestRequest(BaseModel):
    repo_url: str
    collection_name: str


class AnswerRequest(BaseModel):
    user_question: str
    number_of_results: int
    collection_name: str


# Endpoint to ingest a GitHub project
@app.post("/ingest")
def ingest_endpoint(request: IngestRequest):
    ingest_github_project(request.repo_url, request.collection_name)
    return {"status": "success"}


def answer_question(
    user_question: str,
    number_of_results: int,
    collection_name: str,
) -> str:
    try:
        question_embedding = embedder.embed_text(user_question)
        results = db.query_chunks(
            question_embedding, number_of_results, collection_name
        )
        documents = results.get("documents", [[]])

        if not documents or not documents[0]:
            prompt = (
                f"User question:\n{user_question}\n\n"
                "No relevant code context found. Please answer using your general knowledge."
            )
            logging.info(f"User question: {user_question}")
            logging.info("No relevant code snippets found.")
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
            logging.info(f"User question: {user_question}")
            logging.info(f"Most relevant code snippet(s): {context}")

        answer = ollama_client.chat_with_ollama(prompt)
        logging.info(f"LLM answer: {answer}")
        return answer
    except errors.AIServiceError as e:
        logging.error(f"Answer error: {e}")
        raise


# Endpoint to answer a question
@app.post("/answer")
def answer_endpoint(request: AnswerRequest):
    answer = answer_question(
        request.user_question, request.number_of_results, request.collection_name
    )
    return {"answer": answer}


def main() -> None:
    app_port = utils.get_env_var(constants.PORT)
    logging.info(f"Starting server on port {app_port}")
    uvicorn.run(
        "ai_service.main:app",
        host="127.0.0.1",
        port=int(app_port),
        reload=True,
    )


if __name__ == "__main__":
    main()
