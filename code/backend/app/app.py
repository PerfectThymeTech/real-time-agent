import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.api.v1.api_v1 import api_v1_router
from app.core.settings import settings
from app.logs import setup_logging, setup_opentelemetry
from fastapi import FastAPI, Request
from starlette.background import BackgroundTask

MAX_LOGGED_BODY_BYTES = 4096


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gracefully start the application before the server reports readiness.

    :param app: The FastAPI application instance.
    :type app: FastAPI
    :yields: Control back to the caller to start the server.
    :rtype: AsyncGenerator[None, None]
    """
    setup_opentelemetry()
    yield


def get_app() -> FastAPI:
    """Setup the Fast API server.

    :returns: The FastAPI object to start the server.
    :rtype: FastAPI
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.APP_VERSION,
        openapi_url="/openapi.json",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    return app


app = get_app()
logger = setup_logging(__name__)


def log_info(req_headers, req_body, res_body):
    logger.debug(f"Request Headers: {req_headers}")
    logger.debug(f"Request Body: {req_body}")
    logger.debug(f"Response Body: {res_body}")


def _truncate_body(body: bytes) -> bytes:
    if len(body) <= MAX_LOGGED_BODY_BYTES:
        return body
    return body[:MAX_LOGGED_BODY_BYTES]


if settings.LOGGING_LEVEL == logging.DEBUG:

    @app.middleware("http")
    async def some_middleware(request: Request, call_next):
        req_headers = request.headers
        req_body = await request.body()
        truncated_req_body = _truncate_body(req_body)

        async def receive() -> dict:
            return {"type": "http.request", "body": req_body, "more_body": False}

        request = Request(request.scope, receive)
        response = await call_next(request)

        original_body_iterator = response.body_iterator
        response_body_chunks: list[bytes] = []
        captured_response_bytes = 0

        async def tee_body_iterator():
            nonlocal captured_response_bytes
            async for chunk in original_body_iterator:
                if chunk and captured_response_bytes < MAX_LOGGED_BODY_BYTES:
                    remaining_bytes = MAX_LOGGED_BODY_BYTES - captured_response_bytes
                    truncated_chunk = chunk[:remaining_bytes]
                    response_body_chunks.append(truncated_chunk)
                    captured_response_bytes += len(truncated_chunk)
                yield chunk

        response.body_iterator = tee_body_iterator()

        existing_background = response.background

        async def background_with_logging() -> None:
            if existing_background is not None:
                await existing_background()
            log_info(
                req_headers=req_headers,
                req_body=truncated_req_body,
                res_body=b"".join(response_body_chunks),
            )

        response.background = BackgroundTask(background_with_logging)
        return response
