# ruff: noqa: E402


from dotenv import load_dotenv

load_dotenv()
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
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()


def ingest_github_project(repo_url: str, collection_name: str) -> None:
    # Clone the GitHub repository
    project_dir = project_ingestor.clone_github_repo(repo_url)
    try:
        print("Scanning project directory ...")
        code_files = project_ingestor.scan_code_files(project_dir)
        print(f"Found {len(code_files)} code files to process.")

        code_snippets: list[str] = []
        embeddings: list[list[float]] = []

        print("Embedding content for each file ...")
        for file_path in code_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    code = f.read().strip()
                    if not code:
                        print(f"Skipping empty file: {file_path}")
                        continue
                    code_snippets.append(code)
                    embeddings.append(embedder.embed_text(code))
            except FileNotFoundError:
                err = errors.FileReadError.file_not_found(file_path)
                print(f"{err}")
                continue
            except PermissionError:
                err = errors.FileReadError.permission_denied(file_path)
                print(f"{err}")
                continue
            except UnicodeDecodeError:
                err = errors.FileReadError.decode_error(file_path)
                print(f"{err}")
                continue
            except OSError as e:
                err = errors.FileReadError.os_error(file_path, e)
                print(f"{err}")
                continue

        if code_snippets:
            db.add_chunks(code_snippets, embeddings, collection_name)
            print(f"Stored {len(code_snippets)} code snippets in ChromaDB.")
        else:
            print("No valid code snippets found to store.")
    finally:
        print("Cleaning up project directory ...")
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
    try:
        ingest_github_project(request.repo_url, request.collection_name)
        return {"status": "success"}
    except errors.AIServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def answer_question(
    user_question: str, number_of_results: int, collection_name: str
) -> str:
    # Step 1: Embed the user question
    question_embedding = embedder.embed_text(user_question)
    # Step 2: Query ChromaDB for relevant code snippets
    results = db.query_chunks(question_embedding, number_of_results, collection_name)

    # Step 3: Prepare context for the LLM
    documents = results.get("documents", [[]])

    if not documents or not documents[0]:
        prompt = (
            f"User question:\n{user_question}\n\n"
            "No relevant code context found. Please answer using your general knowledge."
        )
        print("User question:", user_question)
        print("\nNo relevant code snippets found.")
    else:
        # Remove duplicate snippets while preserving order
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
        print("User question:", user_question)
        print("\nMost relevant code snippet(s):\n", context)

    # Step 4: Get answer from LLM
    answer = ollama_client.chat_with_ollama(prompt)
    print("\nLLM answer:\n", answer)
    return answer


# Endpoint to answer a question
@app.post("/answer")
def answer_endpoint(request: AnswerRequest):
    try:
        answer = answer_question(
            request.user_question,
            request.number_of_results,
            request.collection_name,
        )
        return {"answer": answer}
    except errors.AIServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    app_port = utils.get_env_var(constants.PORT)
    uvicorn.run(
        "ai_service.main:app", host="127.0.0.1", port=int(app_port), reload=True
    )


if __name__ == "__main__":
    main()
