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
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_refresh(self, user: User, expires: Optional[timedelta] = None) -> RefreshToken:
        token = create_refresh_token()
        expires_at = datetime.now(timezone.utc) + (expires or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        rt = RefreshToken(token=token, user=user, expires_at=expires_at)
        self.session.add(rt)
        await self.session.flush()
        await self.session.commit()
        return rt

    async def rotate_refresh(self, current_token: str) -> RefreshToken:
        rt = await self.repo.get_refresh_by_token(current_token)
        if not rt:
            raise ValueError('invalid_refresh')
        if rt.revoked:
            raise ValueError('revoked')
        if rt.expires_at:
            expires = rt.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if expires < datetime.now(timezone.utc):
                raise ValueError('expired')

        # revoke current
        await self.repo.revoke_refresh(rt)
        await self.session.commit()

        # create new using user_id to avoid lazy-loading user relationship in sync context
        new_token = create_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_rt = RefreshToken(token=new_token, user_id=rt.user_id, expires_at=expires_at)
        self.session.add(new_rt)
        await self.session.flush()
        await self.session.commit()
        return new_rt

    async def logout(self, refresh_token: str):
        rt = await self.repo.get_refresh_by_token(refresh_token)
        if rt:
            await self.repo.revoke_refresh(rt)
            await self.session.commit()
            return True
        return False

    async def change_password(self, user: User, current_password: str, new_password: str):
        if not verify_password(current_password, user.hashed_password):
            raise ValueError('invalid_current_password')
        user.hashed_password = hash_password(new_password)
        self.session.add(user)
        # revoke all refresh tokens
        await self.repo.revoke_all_for_user(user)
        await self.session.commit()
        return True

    # Email verification and password reset flows
    async def send_verification(self, user: User, email_service):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        vt = await self.repo.create_verification_token(user, token, expires_at)
        await self.session.commit()
        link = f"https://example.local/auth/verify?token={token}"
        await email_service.send_email(user.email, "Verify your account", f"Click to verify: {link}")
        return vt

    async def verify_email(self, token: str):
        vt = await self.repo.get_verification_by_token(token)
        if not vt:
            raise ValueError('invalid')
        if vt.used:
            raise ValueError('used')
        if vt.expires_at:
            exp = vt.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise ValueError('expired')
        # mark user verified
        user = await self.repo.get_by_id(vt.user_id)
        user.is_verified = True
        await self.repo.mark_verification_used(vt)
        self.session.add(user)
        await self.session.commit()
        return True

    async def send_password_reset(self, user: User, email_service):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=3)
        pr = await self.repo.create_password_reset(user, token, expires_at)
        await self.session.commit()
        link = f"https://example.local/auth/reset-password?token={token}"
        await email_service.send_email(user.email, "Reset your password", f"Click to reset: {link}")
        return pr

    async def reset_password(self, token: str, new_password: str):
        pr = await self.repo.get_password_reset_by_token(token)
        if not pr:
            raise ValueError('invalid')
        if pr.used:
            raise ValueError('used')
        if pr.expires_at:
            exp = pr.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise ValueError('expired')
        user = await self.repo.get_by_id(pr.user_id)
        user.hashed_password = hash_password(new_password)
        await self.repo.mark_password_reset_used(pr)
        # revoke user refresh tokens
        await self.repo.revoke_all_for_user(user)
        self.session.add(user)
        await self.session.commit()
        return True
