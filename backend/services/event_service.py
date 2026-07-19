from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.event import Event
from repos.event_repo import EventRepository


class EventService:
    def __init__(self, session: AsyncSession):
        self.repo = EventRepository(session)
        self.session = session

    async def get(self, id: str) -> Optional[Event]:
        return await self.repo.get_by_id(id)

    async def get_by_slug(self, slug: str) -> Optional[Event]:
        return await self.repo.get_by_slug(slug)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, event: Event) -> Event:
        ev = await self.repo.create(event)
        await self.session.commit()
        return ev

    async def update(self, event: Event) -> Event:
        ev = await self.repo.update(event)
        await self.session.commit()
        return ev

    async def delete(self, event: Event) -> None:
        await self.repo.delete(event)
        await self.session.commit()
