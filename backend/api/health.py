from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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

    return HealthResponse(status="ok" if ok else "error", version="0.0.0", environment="development", database=ok)
