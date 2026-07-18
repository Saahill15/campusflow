from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from .engine import get_engine


engine = get_engine()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def get_session() -> AsyncSession:
    return async_session()
