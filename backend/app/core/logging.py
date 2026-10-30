"""Centralized logging configuration for the application."""

import logging
import sys
from logging import Formatter

from app.core.settings import get_settings


def setup_logging() -> None:
    """Configure application logging."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    settings = get_settings()

    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(Formatter(log_format))
    logger.addHandler(console_handler)

    # Log initial configuration
    logger.info("Logging configured - Level: %s, Environment: %s", settings.log_level, settings.environment)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name (typically ``__name__``)."""
    return logging.getLogger(name)
