from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from core.logging import setup_logging
from api.health import router as health_router
from api.registration import router as registration_router


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

    # Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

    # Routers
    app.include_router(health_router, prefix="/health", tags=["health"])
    # Auth
    from api.auth import router as auth_router
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(registration_router, prefix="/api/v1", tags=["registration"])
    from api.admin import router as admin_router
    app.include_router(admin_router, prefix="/api/v1")

    return app


app = create_app()

