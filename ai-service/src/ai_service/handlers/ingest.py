import logging
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter

from ai_service import (
    errors,
    project_ingestor,
)
from ai_service.embeddings import encoding
from ai_service.db_setup import set_repo_context, add_chunks

logger = logging.getLogger(__name__)
router = APIRouter()


class IngestRequest(BaseModel):
    canonical_github_url: HttpUrl


def ingest_github_project(canonical_github_url: str) -> None:
    set_repo_context(canonical_github_url)  # Set context once at the start
    project_dir = project_ingestor.clone_github_repo(canonical_github_url)
    try:
        code_files = project_ingestor.scan_code_files(project_dir)
        logger.info(f"Found {len(code_files)} code files to process.")

        code_snippets: list[str] = []

        logger.info("Processing and embedding code files...")
        for file_path in code_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    code = f.read().strip()
                    if not code:
                        logger.warning(f"Skipping empty file: {file_path}")
                        continue
                    code_snippets.append(code)
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
            # Batch embed all documents at once for better performance
            embeddings = encoding.embed_documents(code_snippets)

            add_chunks(code_snippets, embeddings)
            logger.info(f"Stored {len(code_snippets)} code snippets in ChromaDB.")
        else:
            logger.warning("No valid code snippets found to store.")
    finally:
        project_ingestor.cleanup_dir(project_dir)


# Endpoint to ingest a GitHub project
@router.post("/ingest")
def ingest_endpoint(request: IngestRequest) -> JSONResponse:
    ingest_github_project(str(request.canonical_github_url))
    return JSONResponse(
        status_code=201,
        content={
            "message": f"Successfully ingested project: {request.canonical_github_url}",
        },
    )
