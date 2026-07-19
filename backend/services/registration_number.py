from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.registration import Registration


class RegistrationNumberGenerator:
    prefix = 'PG26'

    @classmethod
    async def generate_candidate(cls, session: AsyncSession) -> str:
        q = await session.execute(
            select(Registration.registration_number).where(Registration.registration_number != None)
        )
        nums = []
        for v in q.scalars().all():
            try:
                if v and v.startswith(cls.prefix + '-'):
                    parts = v.split('-')
                    num = int(parts[-1])
                    nums.append(num)
            except Exception:
                continue
        next_num = 1
        if nums:
            next_num = max(nums) + 1
        return f"{cls.prefix}-{next_num:06d}"
