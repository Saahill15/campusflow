from logging.config import fileConfig
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / '.env')

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# set DB url from env
section = config.get_section(config.config_ini_section)
# allow default local sqlite file when DATABASE_URL not provided
raw_url = os.getenv('DATABASE_URL') or section.get('sqlalchemy.url') or 'sqlite:///./dev_auth.db'
if raw_url.startswith('sqlite+aiosqlite://'):
    raw_url = raw_url.replace('sqlite+aiosqlite://', 'sqlite://', 1)
if raw_url.startswith('postgresql://'):
    raw_url = raw_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
if raw_url.startswith('postgres://'):
    raw_url = raw_url.replace('postgres://', 'postgresql+asyncpg://', 1)
section['sqlalchemy.url'] = raw_url


def run_migrations_offline():
    context.configure(url=section['sqlalchemy.url'], target_metadata=None, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    if section['sqlalchemy.url'].startswith('postgresql+asyncpg://'):
        connectable = create_async_engine(section['sqlalchemy.url'], future=True, poolclass=pool.NullPool)

        async def run_async():
            async with connectable.connect() as connection:
                await connection.run_sync(do_run_migrations)
            await connectable.dispose()

        asyncio.run(run_async())
    else:
        connectable = engine_from_config(section, prefix='sqlalchemy.', poolclass=pool.NullPool)
        with connectable.connect() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
