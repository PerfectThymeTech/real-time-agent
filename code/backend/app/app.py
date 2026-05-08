import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.api.v1.api_v1 import api_v1_router
from app.core.settings import settings
from app.logs import setup_logging, setup_opentelemetry
from fastapi import FastAPI, Request, Response
from starlette.background import BackgroundTask


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


def log_info(req_headers, req_body, res_body):
    logger = setup_logging(__name__)
    logger.debug(f"Request Headers: {req_headers}")
    logger.debug(f"Request Body: {req_body}")
    logger.debug(f"Response Body: {res_body}")


if settings.LOGGING_LEVEL == logging.DEBUG:

    @app.middleware("http")
    async def some_middleware(request: Request, call_next):
        req_headers = request.headers
        req_body = await request.body()
        response = await call_next(request)

        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        res_body = b"".join(chunks)

        task = BackgroundTask(log_info, req_headers, req_body, res_body)
        return Response(
            content=res_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=task,
        )
