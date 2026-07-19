from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.event_settings import EventSettings
from repos.event_settings_repo import EventSettingsRepository


class EventSettingsService:
    def __init__(self, session: AsyncSession):
        self.repo = EventSettingsRepository(session)
        self.session = session

    async def get_by_event(self, event_id: str) -> Optional[EventSettings]:
        return await self.repo.get_by_event_id(event_id)

    async def get(self, id: str) -> Optional[EventSettings]:
        return await self.repo.get_by_id(id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, settings: EventSettings) -> EventSettings:
        settings = await self.repo.create(settings)
        await self.session.commit()
        return settings

    async def update(self, settings: EventSettings) -> EventSettings:
        settings = await self.repo.update(settings)
        await self.session.commit()
        return settings

    async def delete(self, settings: EventSettings) -> None:
        await self.repo.delete(settings)
        await self.session.commit()
