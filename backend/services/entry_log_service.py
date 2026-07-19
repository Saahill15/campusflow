from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.entry_log import EntryLog
from repos.entry_log_repo import EntryLogRepository


class EntryLogService:
    def __init__(self, session: AsyncSession):
        self.repo = EntryLogRepository(session)
        self.session = session

    async def get(self, id: str) -> Optional[EntryLog]:
        return await self.repo.get_by_id(id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, entry: EntryLog) -> EntryLog:
        entry = await self.repo.create(entry)
        await self.session.commit()
        return entry

    async def update(self, entry: EntryLog) -> EntryLog:
        entry = await self.repo.update(entry)
        await self.session.commit()
        return entry

    async def delete(self, entry: EntryLog) -> None:
        await self.repo.delete(entry)
        await self.session.commit()
