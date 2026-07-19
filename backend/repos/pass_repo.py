from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.pass_model import Pass


class PassRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: str) -> Optional[Pass]:
        q = await self.session.execute(select(Pass).where(Pass.id == id))
        return q.scalars().first()

    async def get_by_pass_number(self, pass_number: str) -> Optional[Pass]:
        q = await self.session.execute(select(Pass).where(Pass.pass_number == pass_number))
        return q.scalars().first()

    async def get_by_registration(self, registration_id: str) -> Optional[Pass]:
        q = await self.session.execute(select(Pass).where(Pass.registration_id == registration_id))
        return q.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[Pass]:
        q = await self.session.execute(select(Pass).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, p: Pass) -> Pass:
        self.session.add(p)
        await self.session.flush()
        return p

    async def update(self, p: Pass) -> Pass:
        self.session.add(p)
        await self.session.flush()
        return p

    async def delete(self, p: Pass) -> None:
        await self.session.delete(p)
        await self.session.flush()
