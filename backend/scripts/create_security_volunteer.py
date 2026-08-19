import asyncio
import getpass
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.session import async_session
from models.auth import Role, User, users_roles
from services.auth_service import hash_password

ROLE_NAME = 'security_volunteer'


async def get_or_create_role(session: AsyncSession) -> Role:
    role = (await session.execute(select(Role).where(Role.name == ROLE_NAME))).scalars().first()
    if role:
        return role
    role = Role(name=ROLE_NAME, description='On-day QR scanning and check-in role')
    session.add(role)
    await session.flush()
    return role


async def main() -> None:
    email = os.environ.get('SECURITY_VOLUNTEER_EMAIL') or input('Security volunteer email: ').strip()
    password = os.environ.get('SECURITY_VOLUNTEER_PASSWORD') or getpass.getpass('Security volunteer password: ')
    if not email or not password:
        raise SystemExit('Security volunteer email and password are required.')

    async with async_session() as session:
        role = await get_or_create_role(session)
        user = (await session.execute(select(User).where(User.email == email).options(selectinload(User.roles)))).scalars().first()
        if not user:
            user = User(email=email, hashed_password=hash_password(password), is_active=True, is_verified=True)
            session.add(user)
            await session.flush()
        if not any(existing.name == ROLE_NAME for existing in user.roles):
            await session.execute(insert(users_roles).values(user_id=user.id, role_id=role.id))
        await session.commit()
    print(f'Security volunteer role ready for {email}.')


if __name__ == '__main__':
    asyncio.run(main())
