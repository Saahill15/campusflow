import os
import sys
from alembic.config import Config
from alembic import command

here = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.abspath(os.path.join(here, '..', 'alembic_test_abs.db'))
# Force a sync sqlite URL for Alembic to use a synchronous engine
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
# Ensure a fresh DB for each run to validate migrations apply cleanly
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception:
        pass

cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
try:
    command.upgrade(cfg, 'head')
    print('Alembic upgrade head completed')
except Exception as e:
    print('Alembic upgrade failed:', e)
    raise
