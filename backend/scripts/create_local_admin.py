import asyncio
import getpass
import os
import sys
from pathlib import Path

# Ensure backend package imports work when running from scripts directory
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from httpx import AsyncClient, ASGITransport

from app.main import app
from db.session import async_session
from models.auth import User, Role, users_roles
from services.auth_service import hash_password


ADMIN_ROLE_NAME = 'admin'
ENV_EMAIL = 'LOCAL_ADMIN_EMAIL'
ENV_PASSWORD = 'LOCAL_ADMIN_PASSWORD'


def prompt_for_email() -> str:
    env_email = os.environ.get(ENV_EMAIL)
    if env_email:
        return env_email.strip()
    email = input('Admin email: ').strip()
    return email


def prompt_for_password() -> str:
    env_password = os.environ.get(ENV_PASSWORD)
    if env_password:
        return env_password
    return getpass.getpass('Admin password: ')


async def get_or_create_admin_role(session: AsyncSession) -> Role:
    result = await session.execute(select(Role).where(Role.name == ADMIN_ROLE_NAME))
    role = result.scalars().first()
    if role:
        return role

    role = Role(name=ADMIN_ROLE_NAME, description='Local development admin role')
    session.add(role)
    await session.flush()
    return role


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email).options(selectinload(User.roles))
    )
    return result.scalars().first()


async def create_or_get_user(session: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(session, email)
    if user:
        return user

    user = User(email=email, hashed_password=hash_password(password), is_active=True, is_verified=False)
    session.add(user)
    await session.flush()
    return user


async def has_user_role(session: AsyncSession, user: User, role: Role) -> bool:
    q = await session.execute(
        select(users_roles).where(users_roles.c.user_id == user.id, users_roles.c.role_id == role.id)
    )
    return q.first() is not None


async def ensure_role_assigned(session: AsyncSession, user: User, role: Role) -> bool:
    if await has_user_role(session, user, role):
        return False
    await session.execute(
        insert(users_roles).values(user_id=user.id, role_id=role.id)
    )
    return True


async def verify_admin_request(email: str, password: str) -> tuple[bool, str | None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://local') as client:
        login_resp = await client.post('/auth/login', json={'email': email, 'password': password})
        if login_resp.status_code != 200:
            return False, None
        data = login_resp.json().get('data', {})
        token = data.get('access_token')
        if not token:
            return False, None

        admin_resp = await client.get('/api/v1/admin/registrations', headers={'Authorization': f'Bearer {token}'})
        return admin_resp.status_code == 200, token


async def main() -> None:
    email = prompt_for_email()
    if not email:
        raise SystemExit('Admin email is required.')

    password = prompt_for_password()
    if not password:
        raise SystemExit('Admin password is required.')

    async with async_session() as session:
        role = await get_or_create_admin_role(session)
        user = await create_or_get_user(session, email, password)
        assigned = await ensure_role_assigned(session, user, role)
        session.add(user)
        await session.commit()

        # Refresh state after commit
        await session.refresh(user)

        user_has_role = await has_user_role(session, user, role)
        print('Admin seed summary:')
        print(f'  admin user exists: yes ({email})')
        print(f'  admin role exists: yes ({ADMIN_ROLE_NAME})')
        print(f"  admin role assigned to user: {'yes' if user_has_role else 'no'}")

        print('\nVerifying login and admin endpoint access...')
        access_ok, token = await verify_admin_request(email, password)
        if access_ok:
            print('  login succeeded: yes')
            print('  admin registrations endpoint accessible: yes')
        else:
            print('  login succeeded: no')
            print('  admin registrations endpoint accessible: no')
            if token is None:
                print('  note: login failed with the provided credentials or user does not exist.')


if __name__ == '__main__':
    asyncio.run(main())
