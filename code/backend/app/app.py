from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.api.v1.api_v1 import api_v1_router
from app.core.settings import settings
from app.logs import setup_opentelemetry
from fastapi import FastAPI


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
