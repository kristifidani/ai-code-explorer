from pydantic import BaseModel
from fastapi import APIRouter

from ai_service import (
    db,
    embedder,
    errors,
    project_ingestor,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class IngestRequest(BaseModel):
    repo_url: str


def ingest_github_project(repo_url: str) -> None:
    # Generate collection_name from repo_url
    collection_name = db.generate_collection_name(repo_url)
    project_dir = project_ingestor.clone_github_repo(repo_url)
    try:
        code_files = project_ingestor.scan_code_files(project_dir)
        logger.info(f"Found {len(code_files)} code files to process.")

        code_snippets: list[str] = []
        embeddings: list[list[float]] = []

        logger.info("Embedding content for each file ...")
        for file_path in code_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    code = f.read().strip()
                    if not code:
                        logger.warning(f"Skipping empty file: {file_path}")
                        continue
                    code_snippets.append(code)
                    embeddings.append(embedder.embed_text(code))
            except FileNotFoundError:
                err = errors.FileReadError.file_not_found(file_path)
                logger.error(err)
                continue
            except PermissionError:
                err = errors.FileReadError.permission_denied(file_path)
                logger.error(err)
                continue
            except UnicodeDecodeError:
                err = errors.FileReadError.decode_error(file_path)
                logger.error(err)
                continue
            except OSError as e:
                err = errors.FileReadError.os_error(file_path, e)
                logger.error(err)
                continue

        if code_snippets:
            db.add_chunks(code_snippets, embeddings, collection_name)
            logger.info(f"Stored {len(code_snippets)} code snippets in ChromaDB.")
        else:
            logger.warning("No valid code snippets found to store.")
    finally:
        project_ingestor.cleanup_dir(project_dir)


# Endpoint to ingest a GitHub project
@router.post("/ingest", status_code=200)
def ingest_endpoint(request: IngestRequest) -> dict[str, str]:
    ingest_github_project(request.repo_url)
    return {"message": "Successfully ingested project"}
