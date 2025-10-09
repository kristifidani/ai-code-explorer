# ruff: noqa: E402


from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from ai_service import (
    errors,
    utils,
)

# FastAPI imports
from fastapi import FastAPI, Request
import uvicorn

from .handlers import ingest_router, answer_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize services on startup and cleanup on shutdown."""
    is_dev = utils.is_development()

    # Configure ALL logging in one place based on environment
    if not is_dev:  # Production: quiet everything noisy
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("chromadb").setLevel(logging.WARNING)
        logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
        logging.getLogger("transformers").setLevel(logging.WARNING)
        logging.getLogger("torch").setLevel(logging.WARNING)
    # Development: keep all logs verbose for debugging

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


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {"status": "healthy", "service": "ai-service"}


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
    # Check if we're in development or production
    is_dev = utils.is_development()

    try:
        app_port = utils.get_env_var(utils.PORT)
    except errors.NotFound:
        app_port = "8000"
        logger.warning("PORT not set; defaulting to %s", app_port)

    uvicorn.run(
        "ai_service.main:app",
        host="0.0.0.0",
        port=int(app_port),
        reload=is_dev,  # Only reload in development
        log_level="info",  # Keep uvicorn startup logs visible
        access_log=is_dev,  # Show HTTP request logs only in development
    )


if __name__ == "__main__":
    main()
