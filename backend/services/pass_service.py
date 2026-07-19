from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.pass_model import Pass
from repos.pass_repo import PassRepository


class PassService:
    def __init__(self, session: AsyncSession):
        self.repo = PassRepository(session)
        self.session = session

    async def get(self, id: str) -> Optional[Pass]:
        return await self.repo.get_by_id(id)

    async def get_by_pass_number(self, pass_number: str) -> Optional[Pass]:
        return await self.repo.get_by_pass_number(pass_number)

    async def get_by_registration(self, registration_id: str) -> Optional[Pass]:
        return await self.repo.get_by_registration(registration_id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, p: Pass) -> Pass:
        p = await self.repo.create(p)
        await self.session.commit()
        return p

    async def update(self, p: Pass) -> Pass:
        p = await self.repo.update(p)
        await self.session.commit()
        return p

    async def delete(self, p: Pass) -> None:
        await self.repo.delete(p)
        await self.session.commit()
