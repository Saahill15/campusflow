from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from services.auth_service import AuthService, create_access_token
from schemas.common import SuccessResponse
from pydantic import BaseModel, EmailStr, constr

router = APIRouter()


class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.post('/register')
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        user = await svc.register_user(payload.email, payload.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists')
    access = create_access_token(str(user.id))
    return SuccessResponse(data={'access_token': access}).model_dump()


@router.post('/login')
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    user = await svc.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    access = create_access_token(str(user.id))
    rt = await svc.create_refresh(user)
    return SuccessResponse(data={'access_token': access, 'refresh_token': rt.token}).model_dump()


@router.get('/me')
async def me():
    return SuccessResponse(data={'msg': 'not implemented'}).model_dump()
