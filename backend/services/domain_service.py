from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from repos.domain_repo import GenericRepository


class DomainService:
    def __init__(self, model: Type, session: AsyncSession):
        self.repo = GenericRepository(model, session)

    async def get(self, id: str):
        return await self.repo.get_by_id(id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list_all(limit=limit, offset=offset)

    async def create(self, obj):
        return await self.repo.create(obj)

    async def update(self, id: str, **attrs):
        return await self.repo.update(id, **attrs)

    async def soft_delete(self, id: str):
        return await self.repo.soft_delete(id)

    async def hard_delete(self, id: str):
        return await self.repo.hard_delete(id)
