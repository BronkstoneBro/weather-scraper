import sys
from loguru import logger

from .config import settings


def setup_logger():
    logger.remove()

    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        settings.log_file,
        format=settings.log_format,
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    logger.info("Logger initialized")
    logger.debug(f"Log level: {settings.log_level}")
    logger.debug(f"Log file: {settings.log_file}")


setup_logger()
