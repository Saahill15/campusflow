import asyncio
import asyncio
import os
import sys
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Use a file-based sqlite with aiosqlite driver for tests so migrations / create_all are stable
import pathlib
db_file = os.path.abspath('./test_auth.db')
db_file_posix = pathlib.Path(db_file).as_posix()
os.environ.setdefault('DATABASE_URL', f'sqlite+aiosqlite:///{db_file_posix}')

# create tables for tests using sync engine on the same absolute file path
from sqlalchemy import create_engine
from db.base import Base
# Remove existing test DB to ensure clean state
if os.path.exists(db_file):
    os.remove(db_file)

# Ensure models are imported so tables are registered on Base.metadata
import models.auth  # noqa: F401
import models.domain  # noqa: F401
import models.event  # noqa: F401
import models.registration  # noqa: F401
import models.pass_model  # noqa: F401
import models.qr_code  # noqa: F401
import models.gate  # noqa: F401
import models.entry_log  # noqa: F401
import models.event_settings  # noqa: F401

sync_url = f'sqlite:///{db_file_posix}'
sync_engine = create_engine(sync_url, echo=False)
Base.metadata.create_all(bind=sync_engine)

from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def reset_database():
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
