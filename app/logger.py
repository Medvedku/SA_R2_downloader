import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from app.config import get_appdata_dir


_LOGGER_NAME = "sa_r2"


def get_log_path():
    return get_appdata_dir() / "app.log"


def configure_logger() -> Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_path = get_log_path()
    handler = RotatingFileHandler(str(log_path), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # also add a lightweight console handler for development
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


def get_logger() -> Logger:
    return configure_logger()


# Convenience
logger = get_logger()
