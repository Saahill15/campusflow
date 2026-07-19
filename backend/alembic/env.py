from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# set DB url from env
section = config.get_section(config.config_ini_section)
# allow default local sqlite file when DATABASE_URL not provided
section['sqlalchemy.url'] = os.getenv('DATABASE_URL', os.getenv('DATABASE_URL', 'sqlite:///./dev_auth.db'))


def run_migrations_offline():
    context.configure(url=section['sqlalchemy.url'], target_metadata=None, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(section, prefix='sqlalchemy.', poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
