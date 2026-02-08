#!/usr/bin/env python3
"""
Claudememv2 Logger
Centralized logging configuration for all modules.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logger(name: str = "claudememv2") -> logging.Logger:
    """Set up and return a logger that writes to file and stderr.

    Log file: ~/.claude/Claudememv2-data/logs/memory.log
    Console: WARNING and above to stderr
    File: DEBUG and above
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Import here to avoid circular dependency
    from utils import get_home_dir

    # Determine log directory
    log_dir = get_home_dir() / ".claude" / "Claudememv2-data" / "logs"

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "memory.log"

        # File handler: DEBUG and above, with rotation-friendly append
        file_handler = logging.FileHandler(
            log_file, encoding="utf-8", mode="a"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # If we can't write logs, continue without file logging
        pass

    # Console handler: WARNING and above to stderr (don't pollute stdout)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(
        "[%(levelname)s] %(message)s"
    ))
    logger.addHandler(console_handler)

    return logger
