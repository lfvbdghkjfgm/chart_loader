from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import get_logs_dir

LOGGER_NAME = "chart_loader"


def _build_handler(log_file: Path) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    return handler


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False
    log_file = get_logs_dir() / "chart_loader.log"
    logger.addHandler(_build_handler(log_file))
    logger.info("Logger initialized: %s", log_file)
    return logger

