"""Centralized logging for the Agentic Chatbot."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_CONFIGURED = False

DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "agentic-chatbot.log"
DEFAULT_LOG_LEVEL = "INFO"
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_dir: str | None = None,
    log_level: str | None = None,
) -> None:
    """Configure root project logger once (console + rotating file)."""
    global _CONFIGURED

    if _CONFIGURED:
        return

    level_name = (log_level or os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)).upper()
    level = getattr(logging, level_name, logging.INFO)

    directory = Path(log_dir or os.getenv("LOG_DIR", DEFAULT_LOG_DIR))
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / DEFAULT_LOG_FILE

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    root_logger = logging.getLogger("agentic_chatbot")
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.propagate = False

    _CONFIGURED = True
    root_logger.info(
        "Logging initialized | level=%s | file=%s",
        level_name,
        log_path.resolve(),
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger under the project namespace.

    Example:
        logger = get_logger(__name__)
    """
    setup_logging()

    if name.startswith("agentic_chatbot"):
        return logging.getLogger(name)

    return logging.getLogger(f"agentic_chatbot.{name}")
