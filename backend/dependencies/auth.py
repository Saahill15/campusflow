from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from dependencies.database import get_db
from repos.auth_repo import AuthRepository
from models.auth import User


async def _get_user_from_token(token: str, db: AsyncSession) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    repo = AuthRepository(db)
    user = await repo.get_by_id(int(sub))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_user(token: str = Depends(lambda: None), db: AsyncSession = Depends(get_db)) -> User:
    # token should be provided via Authorization header; FastAPI will normally supply it via a dependency
    # here we expect the caller to wire the token (router dependencies will pass it)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return await _get_user_from_token(token, db)


async def current_user_from_header(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1]
    return await _get_user_from_token(token, db)


async def current_active_user(user: User = Depends(current_user_from_header)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


async def current_verified_user(user: User = Depends(current_active_user)) -> User:
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    return user


class RequireRole:
    def __init__(self, role_name: str):
        self.role_name = role_name

    async def __call__(self, user: User = Depends(current_active_user)) -> User:
        names = {r.name for r in user.roles}
        if self.role_name not in names:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user


class RequireAnyRole:
    def __init__(self, *role_names: str):
        self.role_names = set(role_names)

    async def __call__(self, user: User = Depends(current_active_user)) -> User:
        names = {r.name for r in user.roles}
        if not (names & self.role_names):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user


class RequirePermission:
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    async def __call__(self, user: User = Depends(current_active_user)) -> User:
        # Check permissions via roles
        perms = {p.name for r in user.roles for p in r.permissions}
        if self.permission_name not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission")
        return user
