from fastapi import FastAPI

from app.api.v1.discovery import router as discovery_router
from app.api.v1.health import router as health_router
from app.api.v1.institutions import router as institutions_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="Research Cold Emailer API", version="1.0.0")

    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(institutions_router, prefix=settings.api_v1_prefix)
    app.include_router(discovery_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
