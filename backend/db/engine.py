from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from core.config import settings


def get_engine() -> AsyncEngine:
    return create_async_engine(settings.DATABASE_URL, future=True)
