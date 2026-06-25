from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt: str) -> None:
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.blue + self.fmt + self.reset,
            logging.INFO: self.grey + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(
    name: str = "birthday_bot",
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_dir: str | None = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    fmt = "%(asctime)s|%(levelname)-7s|%(funcName)s| %(message)s"

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(CustomFormatter(fmt))
    logger.addHandler(stdout_handler)

    if log_to_file:
        if log_dir is None:
            log_dir = str(Path(__file__).resolve().parent.parent / "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "birthday_bot.log")

        file_handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(file_handler)

    return logger
