import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File (rotating)
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(logs_dir / "app.log", maxBytes=1_000_000, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
