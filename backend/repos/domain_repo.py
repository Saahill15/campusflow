from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update
from db.base import Base

T = TypeVar('T', bound=Base)


class GenericRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: str) -> Optional[T]:
        q = await self.session.execute(select(self.model).where(self.model.id == id))
        return q.scalars().first()

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        q = await self.session.execute(select(self.model).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, id: str, **attrs) -> Optional[T]:
        obj = await self.get_by_id(id)
        if not obj:
            return None
        for k, v in attrs.items():
            setattr(obj, k, v)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def soft_delete(self, id: str) -> bool:
        obj = await self.get_by_id(id)
        if not obj:
            return False
        obj.is_active = False
        from datetime import datetime, timezone
        obj.deleted_at = datetime.now(timezone.utc)
        self.session.add(obj)
        await self.session.flush()
        return True

    async def hard_delete(self, id: str) -> bool:
        obj = await self.get_by_id(id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True
