import sys

from loguru import logger


def setup_logger(name: str, **kwargs):
    logger.remove()
    logger.add(sys.stdout, colorize=True, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[name]} | {message}")
    return logger.bind(name=name)


def get_logger(name: str = "default") -> logger:
    return setup_logger(name=name)
