# ruff: noqa: E402

from dotenv import load_dotenv

load_dotenv()
from ai_service import (
    db,
    embedder,
    # ollama_client,
    errors,
    project_ingestor,
)


def ingest_github_project(repo_url):
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
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read().strip()
                    if not code:
                        print(f"Skipping empty file: {file_path}")
                        continue
                    code_snippets.append(code)
                    embeddings.append(embedder.embed_text(code))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

        if code_snippets:
            db.add_chunks(code_snippets, embeddings)
            print(f"Stored {len(code_snippets)} code snippets in ChromaDB.")
        else:
            print("No valid code snippets found to store.")
    finally:
        print("Cleaning up project directory ...")
        project_ingestor.cleanup_dir(project_dir)


def main() -> None:
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
