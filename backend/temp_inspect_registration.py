import asyncio
from sqlalchemy import select
from db.session import async_session
from models.registration import Registration

TEST_EMAIL = 'sahililiyaskhan@gmail.com'

async def main():
    async with async_session() as session:
        q = await session.execute(select(Registration).where(Registration.email == TEST_EMAIL))
        rows = q.scalars().all()
        print(f'Found {len(rows)} registrations for {TEST_EMAIL}')
        for reg in rows:
            print('id=', reg.id)
            print('registration_number=', reg.registration_number)
            print('status=', reg.status)
            print('roll_number=', reg.roll_number)
            print('phone=', reg.phone)
            print('created_at=', reg.created_at)
            print('approved_by=', reg.approved_by)
            print('rejected_reason=', reg.rejected_reason)
            print('email=', reg.email)
            print('event_id=', reg.event_id)
            print('---')

asyncio.run(main())
