from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.gate import Gate
from repos.gate_repo import GateRepository


class GateService:
    def __init__(self, session: AsyncSession):
        self.repo = GateRepository(session)
        self.session = session

    async def get(self, id: str) -> Optional[Gate]:
        return await self.repo.get_by_id(id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, gate: Gate) -> Gate:
        gate = await self.repo.create(gate)
        await self.session.commit()
        return gate

    async def update(self, gate: Gate) -> Gate:
        gate = await self.repo.update(gate)
        await self.session.commit()
        return gate

    async def delete(self, gate: Gate) -> None:
        await self.repo.delete(gate)
        await self.session.commit()
