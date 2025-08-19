# ruff: noqa: E402


from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import logging

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from ai_service import (
    errors,
    utils,
    constants,
)

# FastAPI imports
from fastapi import FastAPI, Request
import uvicorn

from .handlers import ingest_router, answer_router

app = FastAPI()
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
