# ruff: noqa: E402

from dotenv import load_dotenv

load_dotenv()
from ai_service import (
    db,
    embedder,
    ollama_client,
    errors,
    project_ingestor,
)


def ingest_github_project(repo_url: str) -> None:
    # Clone the GitHub repository
    project_dir = project_ingestor.clone_github_repo(repo_url)
    try:
        print("Scanning project directory ...")
        code_files = project_ingestor.scan_code_files(project_dir)
        print(f"Found {len(code_files)} code files to process.")

        code_snippets = []
        embeddings = []

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
            except (
                OSError,
                UnicodeDecodeError,
                FileNotFoundError,
                PermissionError,
            ) as e:
                print(f"Error reading {file_path}: {e}")
                continue

        if code_snippets:
            db.add_chunks(code_snippets, embeddings)
            print(f"Stored {len(code_snippets)} code snippets in ChromaDB.")
        else:
            print("No valid code snippets found to store.")
    finally:
        print("Cleaning up project directory ...")
        project_ingestor.cleanup_dir(project_dir)


def answer_question(user_question: str, top_k: int = 3) -> None:
    # Step 1: Embed the user question
    question_embedding = embedder.embed_text(user_question)
    # Step 2: Query ChromaDB for relevant code snippets
    results = db.query_chunks(question_embedding, number_of_results=top_k)

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


def main() -> None:
    try:
        repo_url = "https://github.com/kristifidani/rust_grpc_poc.git"
        ingest_github_project(repo_url)
        answer_question("What is this project about? How does it work?")
    except errors.AIServiceError as e:
        print(f"AI Service error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
