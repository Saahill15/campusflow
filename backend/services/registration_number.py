from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.registration import Registration


class RegistrationNumberGenerator:
    prefix = 'PG26'

    @classmethod
    async def generate_candidate(cls, session: AsyncSession) -> str:
        query = (
            select(Registration.registration_number)
            .where(Registration.registration_number != None)
            .where(Registration.registration_number.like(f'{cls.prefix}-%'))
            .order_by(Registration.registration_number.desc())
            .limit(1)
        )
        q = await session.execute(query)
        last_value = q.scalar_one_or_none()

        next_num = 1
        if last_value:
            try:
                parts = last_value.split('-')
                next_num = int(parts[-1]) + 1
            except Exception:
                next_num = 1
        return f"{cls.prefix}-{next_num:06d}"
