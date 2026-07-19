from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.event_settings import EventSettings


class EventSettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: str) -> Optional[EventSettings]:
        q = await self.session.execute(select(EventSettings).where(EventSettings.id == id))
        return q.scalars().first()

    async def get_by_event_id(self, event_id: str) -> Optional[EventSettings]:
        q = await self.session.execute(select(EventSettings).where(EventSettings.event_id == event_id))
        return q.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[EventSettings]:
        q = await self.session.execute(select(EventSettings).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, settings: EventSettings) -> EventSettings:
        self.session.add(settings)
        await self.session.flush()
        return settings

    async def update(self, settings: EventSettings) -> EventSettings:
        self.session.add(settings)
        await self.session.flush()
        return settings

    async def delete(self, settings: EventSettings) -> None:
        await self.session.delete(settings)
        await self.session.flush()
