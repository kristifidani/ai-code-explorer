# ruff: noqa: E402


from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)
# Suppress the model loading warnings
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

from ai_service import (
    errors,
    utils,
    constants,
)

# FastAPI imports
from fastapi import FastAPI, Request
import uvicorn

from .handlers import ingest_router, answer_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize services on startup and cleanup on shutdown."""

    # Initialize ChromaDB
    logger.info("Initializing ChromaDB...")
    from ai_service.db_setup import initialize_db

    initialize_db()

    # Initialize SentenceTransformer model
    logger.info("Loading embedding model...")
    from ai_service.embeddings import initialize_model

    initialize_model()

    yield

    logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)
app.include_router(ingest_router)
app.include_router(answer_router)


# FastAPI exception handlers
@app.exception_handler(errors.AIServiceError)
async def ai_service_error_handler(
    _request: Request, exc: errors.AIServiceError
) -> JSONResponse:
    status_code = 404 if isinstance(exc, errors.NotFound) else 400
    logger.error("AIServiceError: %s", exc)
    return JSONResponse(
        status_code=status_code,
        content={"error": str(exc), "code": exc.__class__.__name__},
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unexpected error")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "code": "InternalError"},
    )


def main() -> None:
    app_port = utils.get_env_var(constants.PORT)
    uvicorn.run(
        "ai_service.main:app",
        host="127.0.0.1",
        port=int(app_port),
        reload=True,
    )


if __name__ == "__main__":
    main()
