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


def upload_code(code: str) -> None:
    embedding = embedder.embed_text(code)
    db.add_chunks([code], [embedding])


def answer_question(user_question: str, top_k: int = 3) -> None:
    question_embedding = embedder.embed_text(user_question)
    results = db.query_chunks(question_embedding, number_of_results=top_k)

    # Validate query results
    if not results.get("documents") or not results["documents"][0]:
        print("User question:", user_question)
        print("\nNo relevant code snippets found.")
        print(
            "\nLLM answer: I couldn't find any relevant code snippets to answer your question."
        )
        return

    unique_snippets = list(dict.fromkeys(results["documents"][0]))
    relevant_code = "\n---\n".join(unique_snippets)
    prompt = f"User input:\n{relevant_code}\nQuestions: {user_question}\nAsk the user's question based on their input. If not input provided, answer the question based on your general knowledge."
    answer = ollama_client.chat_with_ollama(prompt)
    print("User question:", user_question)
    print("\nMost relevant code snippet(s):\n", relevant_code)
    print("\nLLM answer:\n", answer)


def ingest_github_project(repo_url):
    # Step 1: Clone the repo
    project_dir = project_ingestor.clone_github_repo(repo_url)
    try:
        # Step 2: Scan for code files
        code_files = project_ingestor.scan_code_files(project_dir)
        print(f"Found {len(code_files)} code files:")
        for f in code_files:
            print(f)
        # Step 3: (Optional) Pass code_files to your embedding/storage logic here
        # Example:
        # for file_path in code_files:
        #     with open(file_path, "r") as f:
        #         code = f.read()
        #         # embed and store code...
    finally:
        # Step 4: Clean up
        project_ingestor.cleanup_dir(project_dir)


def main() -> None:
    # code = """"""

    try:
        repo_url = "https://github.com/kristifidani/rust_grpc_poc.git"
        ingest_github_project(repo_url)
    except errors.AIServiceError as e:
        print(f"AI Service error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
