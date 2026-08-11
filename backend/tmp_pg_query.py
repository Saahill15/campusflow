import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings

async def main():
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async with engine.connect() as conn:
        version = (await conn.execute(text('SELECT version_num FROM alembic_version'))).scalar_one_or_none()
        print('REVISION:' + str(version))
        tables = [row[0] for row in (await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))).all()]
        print('TABLES:' + ','.join(tables))
        indexes = [row[0] for row in (await conn.execute(text("SELECT indexname FROM pg_indexes WHERE schemaname='public' ORDER BY indexname"))).all()]
        print('INDEXES:' + ','.join(indexes))
    await engine.dispose()

asyncio.run(main())
