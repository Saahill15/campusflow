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

    async def get_by_id(self, user_id: int) -> Optional[User]:
        from sqlalchemy.orm import selectinload
        from models.auth import Role

        q = await self.session.execute(
            select(User).where(User.id == user_id).options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )
        return q.scalars().first()

    async def get_refresh_by_token(self, token: str):
        from models.auth import RefreshToken
        q = await self.session.execute(select(RefreshToken).where(RefreshToken.token == token))
        return q.scalars().first()

    async def revoke_refresh(self, rt):
        rt.revoked = True
        self.session.add(rt)
        await self.session.flush()
        return rt

    async def revoke_all_for_user(self, user: User):
        from models.auth import RefreshToken
        q = await self.session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
        rts = q.scalars().all()
        for rt in rts:
            rt.revoked = True
            self.session.add(rt)
        await self.session.flush()
        return rts

    async def create_refresh(self, user: User, token: str, expires_at):
        from models.auth import RefreshToken
        rt = RefreshToken(token=token, user=user, expires_at=expires_at)
        self.session.add(rt)
        await self.session.flush()
        return rt

    async def create_verification_token(self, user: User, token: str, expires_at):
        from models.auth import VerificationToken
        vt = VerificationToken(token=token, user_id=user.id, expires_at=expires_at)
        self.session.add(vt)
        await self.session.flush()
        return vt

    async def get_verification_by_token(self, token: str):
        from models.auth import VerificationToken
        q = await self.session.execute(select(VerificationToken).where(VerificationToken.token == token))
        return q.scalars().first()

    async def mark_verification_used(self, vt):
        vt.used = True
        self.session.add(vt)
        await self.session.flush()
        return vt

    async def create_password_reset(self, user: User, token: str, expires_at):
        from models.auth import PasswordResetToken
        pr = PasswordResetToken(token=token, user_id=user.id, expires_at=expires_at)
        self.session.add(pr)
        await self.session.flush()
        return pr

    async def get_password_reset_by_token(self, token: str):
        from models.auth import PasswordResetToken
        q = await self.session.execute(select(PasswordResetToken).where(PasswordResetToken.token == token))
        return q.scalars().first()

    async def mark_password_reset_used(self, pr):
        pr.used = True
        self.session.add(pr)
        await self.session.flush()
        return pr
