from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.event import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: str) -> Optional[Event]:
        q = await self.session.execute(select(Event).where(Event.id == id))
        return q.scalars().first()

    async def get_by_slug(self, slug: str) -> Optional[Event]:
        q = await self.session.execute(select(Event).where(Event.slug == slug))
        return q.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[Event]:
        q = await self.session.execute(select(Event).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, event: Event) -> Event:
        self.session.add(event)
        await self.session.flush()
        return event

    async def update(self, event: Event) -> Event:
        self.session.add(event)
        await self.session.flush()
        return event

    async def delete(self, event: Event) -> None:
        await self.session.delete(event)
        await self.session.flush()
