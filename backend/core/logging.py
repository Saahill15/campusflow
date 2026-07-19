import logging
import sys
from logging.config import dictConfig


def setup_logging():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
    dictConfig(config)
