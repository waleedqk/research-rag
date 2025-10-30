"""Structured logging helpers for the assistant."""
import sys
from loguru import logger

def configure_logging(debug: bool = False) -> None:
    """Configure loguru-based logging."""
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(sys.stderr, level=level)


def get_logger(name: str):
    """Acquire a configured logger instance."""
    return logger.bind(name=name)
