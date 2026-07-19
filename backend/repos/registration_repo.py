from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.registration import Registration


class RegistrationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: str) -> Optional[Registration]:
        q = await self.session.execute(select(Registration).where(Registration.id == id))
        return q.scalars().first()

    async def get_by_registration_number(self, registration_number: str) -> Optional[Registration]:
        q = await self.session.execute(select(Registration).where(Registration.registration_number == registration_number))
        return q.scalars().first()

    async def get_by_user_and_event(self, user_id: int, event_id: str) -> Optional[Registration]:
        q = await self.session.execute(select(Registration).where(Registration.user_id == user_id, Registration.event_id == event_id))
        return q.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[Registration]:
        q = await self.session.execute(select(Registration).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, reg: Registration) -> Registration:
        self.session.add(reg)
        await self.session.flush()
        return reg

    async def update(self, reg: Registration) -> Registration:
        self.session.add(reg)
        await self.session.flush()
        return reg

    async def delete(self, reg: Registration) -> None:
        await self.session.delete(reg)
        await self.session.flush()
