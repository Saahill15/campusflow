import os
import sys
from alembic.config import Config
from alembic import command

here = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.abspath(os.path.join(here, '..', 'alembic_test_abs.db'))
os.environ.setdefault('DATABASE_URL', f'sqlite:///{db_path}')

cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
try:
    command.upgrade(cfg, 'head')
    print('Alembic upgrade head completed')
except Exception as e:
    print('Alembic upgrade failed:', e)
    raise
