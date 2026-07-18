from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import secrets

from passlib.context import CryptContext
from jose import jwt

from sqlalchemy.ext.asyncio import AsyncSession

from repos.auth_repo import AuthRepository
from models.auth import User, RefreshToken
from core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    exp_dt = now + (expires_delta or timedelta(minutes=15))
    payload = {"sub": subject, "exp": int(exp_dt.timestamp()), "iat": int(now.timestamp())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = AuthRepository(session)
        self.session = session

    async def register_user(self, email: str, password: str) -> User:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError('email_exists')

        user = User(email=email, hashed_password=hash_password(password), is_active=True, is_verified=False)
        await self.repo.create_user(user)
        await self.session.commit()
        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_refresh(self, user: User, expires: Optional[timedelta] = None) -> RefreshToken:
        token = create_refresh_token()
        rt = RefreshToken(token=token, user=user, expires_at=(datetime.now(timezone.utc) + (expires or timedelta(days=30))))
        self.session.add(rt)
        await self.session.flush()
        await self.session.commit()
        return rt
