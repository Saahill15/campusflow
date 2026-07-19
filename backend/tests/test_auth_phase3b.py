import pytest
from httpx import AsyncClient
from sqlalchemy import select
from models.auth import VerificationToken, PasswordResetToken, RefreshToken, Role, Permission
from repos.auth_repo import AuthRepository
from db.base import Base
from db.session import get_session
import asyncio


@pytest.mark.asyncio
async def test_refresh_and_logout_and_me(client: AsyncClient):
    # register
    r = await client.post('/auth/register', json={'email': 'user1@example.com', 'password': 'strongPass1'})
    assert r.status_code == 200
    data = r.json()['data']
    access = data['access_token']

    # login to get refresh
    r = await client.post('/auth/login', json={'email': 'user1@example.com', 'password': 'strongPass1'})
    assert r.status_code == 200
    data = r.json()['data']
    rt = data['refresh_token']

    # refresh -> rotate
    r = await client.post('/auth/refresh', json={'refresh_token': rt})
    assert r.status_code == 200
    new_rt = r.json()['data']['refresh_token']
    assert new_rt != rt

    # old token should be revoked (attempt rotate should fail)
    r = await client.post('/auth/refresh', json={'refresh_token': rt})
    assert r.status_code == 401

    # logout with new token
    r = await client.post('/auth/logout', json={'refresh_token': new_rt})
    assert r.status_code == 200

    # refresh should now fail
    r = await client.post('/auth/refresh', json={'refresh_token': new_rt})
    assert r.status_code == 401

    # me endpoint with access token
    headers = {'Authorization': f'Bearer {access}'}
    r = await client.get('/auth/me', headers=headers)
    assert r.status_code == 200
    j = r.json()['data']
    assert j['email'] == 'user1@example.com'


@pytest.mark.asyncio
async def test_change_password_and_revokes(client: AsyncClient):
    # register and login
    await client.post('/auth/register', json={'email': 'user2@example.com', 'password': 'strongPass2'})
    r = await client.post('/auth/login', json={'email': 'user2@example.com', 'password': 'strongPass2'})
    data = r.json()['data']
    rt = data['refresh_token']

    # change password
    headers = {'Authorization': f'Bearer {data["access_token"]}'}
    r = await client.post('/auth/change-password', json={'current_password': 'strongPass2', 'new_password': 'NewStrong3'}, headers=headers)
    assert r.status_code == 200

    # old refresh should be revoked
    r = await client.post('/auth/refresh', json={'refresh_token': rt})
    assert r.status_code == 401

    # login with old password should fail
    r = await client.post('/auth/login', json={'email': 'user2@example.com', 'password': 'strongPass2'})
    assert r.status_code == 401

    # login with new password should work
    r = await client.post('/auth/login', json={'email': 'user2@example.com', 'password': 'NewStrong3'})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_verify_and_password_reset(client: AsyncClient):
    # register
    await client.post('/auth/register', json={'email': 'user3@example.com', 'password': 'strongPass3'})
    # resend verification
    # get db session
    async with get_session() as s:
        repo = AuthRepository(s)
        user = await repo.get_by_email('user3@example.com')
        assert user is not None
        # send verification
        from services.auth_service import AuthService
        svc = AuthService(s)
        from services.email_service import ConsoleEmailService
        email_service = ConsoleEmailService()
        await svc.send_verification(user, email_service)
        # find token
        q = await s.execute(select(VerificationToken).where(VerificationToken.user_id == user.id))
        vt = q.scalars().first()
        assert vt is not None
        # verify
        await svc.verify_email(vt.token)
        # check user is_verified
        user = await repo.get_by_email('user3@example.com')
        assert user.is_verified

        # password reset
        await svc.send_password_reset(user, email_service)
        q = await s.execute(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
        pr = q.scalars().first()
        assert pr is not None
        await svc.reset_password(pr.token, 'ResetPass4')
        # login with new password
    r = await client.post('/auth/login', json={'email': 'user3@example.com', 'password': 'ResetPass4'})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_rbac_permission_dependency(client: AsyncClient):
    # register
    await client.post('/auth/register', json={'email': 'permuser@example.com', 'password': 'strongPass5'})
    r = await client.post('/auth/login', json={'email': 'permuser@example.com', 'password': 'strongPass5'})
    data = r.json()['data']
    access = data['access_token']

    # create role and permission and assign to user
    async with get_session() as s:
        from sqlalchemy.orm import selectinload
        repo = AuthRepository(s)
        user = await repo.get_by_email('permuser@example.com')
        role = Role(name='test_role')
        perm = Permission(name='test_perm')
        role.permissions.append(perm)
        # associate role with user by appending to role.users to avoid lazy-load on user.roles
        role.users.append(user)
        s.add(role)
        s.add(perm)
        await s.flush()
        await s.commit()

    # add a temporary protected endpoint
    from dependencies.auth import RequirePermission
    from app.main import app
    from fastapi import Depends

    @app.get('/test/protected')
    async def protected(u=Depends(RequirePermission('test_perm'))):
        return {'ok': True}

    headers = {'Authorization': f'Bearer {access}'}
    r = await client.get('/test/protected', headers=headers)
    assert r.status_code == 200

