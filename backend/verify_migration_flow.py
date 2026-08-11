import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, os.getcwd())
from db.base import Base
from models.registration import Registration
import models.auth  # noqa: F401
import models.domain  # noqa: F401
import models.event  # noqa: F401
import models.registration  # noqa: F401
import models.pass_model  # noqa: F401
import models.qr_code  # noqa: F401
import models.gate  # noqa: F401
import models.entry_log  # noqa: F401
import models.event_settings  # noqa: F401
from app.main import app

os.environ.setdefault('DATABASE_URL', 'sqlite:///./migration_test.db')

async def main() -> None:
    # ensure DB exists and migrations applied (migration_test.db should already be created by alembic)
    async with create_async_engine(os.environ['DATABASE_URL'], future=True).begin() as conn:
        await conn.run_sync(Base.metadata.reflect)

    with patch('api.registration.email_service.send_email', new_callable=AsyncMock) as mock_send:
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            payload = {
                'first_name': 'Test',
                'last_name': 'User',
                'department': 'Computer Science',
                'academic_year': 'First Year',
                'roll_number': 'CS26001',
                'phone': '9999999999',
                'email': 'testuser@example.com',
                'gender': 'Other',
            }
            r = await client.post('/api/v1/registration', json=payload)
            print('status', r.status_code)
            print('response', r.json())
            print('email_called', mock_send.await_count)

    sync_engine = create_engine('sqlite:///./migration_test.db', echo=False)
    with sync_engine.connect() as conn:
        row = conn.execute(select(Registration)).fetchone()
        print('row_exists', row is not None)
        if row:
            print('row', dict(row._mapping))

if __name__ == '__main__':
    asyncio.run(main())
