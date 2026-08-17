from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from dependencies.database import get_db
from schemas.common import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    ok = True
    try:
        await db.execute(text('SELECT 1'))
    except Exception:
        ok = False

    return HealthResponse(
        status="ok" if ok else "error",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database=ok,
    )


@router.get("/config")
async def health_config() -> dict[str, str | bool]:
    return {
        "config_source": settings.__class__.__module__,
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "database_configured": bool(settings.DATABASE_URL),
        "secret_configured": bool(settings.SECRET_KEY),
        "trusted_hosts_configured": bool(settings.TRUSTED_HOSTS),
        "cors_configured": bool(settings.CORS_ALLOWED_ORIGINS),
    }
