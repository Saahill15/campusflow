import asyncio
from db.session import async_session
from models.auth import User, Role
from sqlalchemy import select

async def main():
    async with async_session() as session:
        result = await session.execute(select(Role).where(Role.name == 'admin'))
        admin_role = result.scalars().first()
        print('admin_role_exists=' + ('yes' if admin_role else 'no'))
        if admin_role:
            result = await session.execute(select(User).join(User.roles).where(Role.name == 'admin'))
            users = result.scalars().all()
            print('admin_users=' + ','.join(user.email for user in users))

asyncio.run(main())
