from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.auth import User


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        q = await self.session.execute(select(User).where(User.email == email))
        return q.scalars().first()

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user
