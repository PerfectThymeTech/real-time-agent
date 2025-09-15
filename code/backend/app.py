from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

from core.settings import settings
from api.v1.api_v1 import api_v1_router
from utils import setup_opentelemetry

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gracefully start the application before the server reports readiness."""
    setup_opentelemetry(app=app)
    yield
    pass


def get_app() -> FastAPI:
    """Setup the Fast API server.

    RETURNS (FastAPI): The FastAPI object to start the server.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="",
        version=settings.APP_VERSION,
        openapi_url="/openapi.json",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    return app


app = get_app()
