from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config


ROOT_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = ROOT_DIR / 'alembic.ini'


def main() -> int:
    os.chdir(ROOT_DIR)
    config = Config(str(ALEMBIC_INI))
    command.upgrade(config, 'head')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
