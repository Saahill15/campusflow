from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.gate import Gate


class GateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: str) -> Optional[Gate]:
        q = await self.session.execute(select(Gate).where(Gate.id == id))
        return q.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[Gate]:
        q = await self.session.execute(select(Gate).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, gate: Gate) -> Gate:
        self.session.add(gate)
        await self.session.flush()
        return gate

    async def update(self, gate: Gate) -> Gate:
        self.session.add(gate)
        await self.session.flush()
        return gate

    async def delete(self, gate: Gate) -> None:
        await self.session.delete(gate)
        await self.session.flush()
