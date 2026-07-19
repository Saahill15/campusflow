from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.entry_log import EntryLog


class EntryLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: str) -> Optional[EntryLog]:
        q = await self.session.execute(select(EntryLog).where(EntryLog.id == id))
        return q.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[EntryLog]:
        q = await self.session.execute(select(EntryLog).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, entry: EntryLog) -> EntryLog:
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def update(self, entry: EntryLog) -> EntryLog:
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def delete(self, entry: EntryLog) -> None:
        await self.session.delete(entry)
        await self.session.flush()
