from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from services.auth_service import AuthService, create_access_token
from schemas.common import SuccessResponse
from pydantic import BaseModel, EmailStr, constr
from dependencies.auth import current_active_user, current_verified_user, current_user_from_header
from services.email_service import ConsoleEmailService

email_service = ConsoleEmailService()

router = APIRouter()


class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: constr(min_length=8)


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


@router.post('/refresh')
async def refresh(payload: RefreshIn, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        new_rt = await svc.rotate_refresh(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    access = create_access_token(str(new_rt.user_id))
    return SuccessResponse(data={'access_token': access, 'refresh_token': new_rt.token}).model_dump()


@router.post('/logout')
async def logout(payload: RefreshIn, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    ok = await svc.logout(payload.refresh_token)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid refresh token')
    return SuccessResponse(data={'msg': 'logged out'}).model_dump()


@router.get('/me')
async def me(user=Depends(current_active_user)):
    # return basic profile and roles/permissions
    perms = {p.name for r in user.roles for p in r.permissions}
    roles = [r.name for r in user.roles]
    data = {
        'id': user.id,
        'email': user.email,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'roles': roles,
        'permissions': list(perms),
    }
    return SuccessResponse(data=data).model_dump()


@router.post('/change-password')
async def change_password(payload: ChangePasswordIn, user=Depends(current_active_user), db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        await svc.change_password(user, payload.current_password, payload.new_password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid current password')
    return SuccessResponse(data={'msg': 'password_changed'}).model_dump()


@router.post('/verify-email')
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        await svc.verify_email(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return SuccessResponse(data={'msg': 'verified'}).model_dump()


@router.post('/resend-verification')
async def resend_verification(db: AsyncSession = Depends(get_db), user=Depends(current_active_user)):
    svc = AuthService(db)
    await svc.send_verification(user, email_service)
    return SuccessResponse(data={'msg': 'sent'}).model_dump()


@router.post('/forgot-password')
async def forgot_password(email: EmailStr, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    # find user
    from repos.auth_repo import AuthRepository
    repo = AuthRepository(db)
    user = await repo.get_by_email(email)
    if user:
        await svc.send_password_reset(user, email_service)
    # always return success to avoid user enumeration
    return SuccessResponse(data={'msg': 'sent'}).model_dump()


@router.post('/reset-password')
async def reset_password(token: str, new_password: constr(min_length=8), db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        await svc.reset_password(token, new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return SuccessResponse(data={'msg': 'password_reset'}).model_dump()
