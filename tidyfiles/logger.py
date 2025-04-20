import sys
from enum import Enum
from pathlib import Path
from typing import Optional
from loguru import logger


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Constants
CONSOLE_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

FILE_LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


def get_logger(
    log_file_path: Path,
    enable_console_logging: bool = True,
    enable_file_logging: bool = True,
    console_log_level: str = LogLevel.WARNING,
    file_log_level: str = LogLevel.INFO,
    file_mode: str = "a",
    rotation: str = "50 MB",
    retention: str = "10 days",
    **kwargs,
) -> Optional[logger]:
    """
    Creates and configures a logger with console and/or file output.

    Args:
        log_file_path: Path to the log file
        enable_console_logging: Enable logging to console
        enable_file_logging: Enable logging to file
        console_log_level: Console logging level (DEBUG|INFO|WARNING|ERROR|CRITICAL)
        file_log_level: File logging level (DEBUG|INFO|WARNING|ERROR|CRITICAL)
        file_mode: File open mode ('a' for append, 'w' for write)
        rotation: When to rotate the log file (e.g., "50 MB", "1 day")
        retention: How long to keep log files (e.g., "10 days")
        **kwargs: Additional logger configuration options

    Returns:
        Configured logger instance or None if no logging is enabled

    Raises:
        ValueError: If log levels are invalid or log path is a directory
    """
    # Validate inputs
    if not isinstance(console_log_level, LogLevel):
        console_log_level = LogLevel(console_log_level.upper())
    if not isinstance(file_log_level, LogLevel):
        file_log_level = LogLevel(file_log_level.upper())

    if file_mode not in {"a", "w"}:
        raise ValueError("file_mode must be 'a' or 'w'")

    if enable_file_logging:
        if log_file_path.is_dir():
            raise ValueError("log_file_path must be a file path, not a directory")
        # Resolve path to handle symlinks
        log_file_path = log_file_path.resolve()

    if not (enable_console_logging or enable_file_logging):
        return None

    # Configure logger
    logger.remove()  # remove default handlers

    if enable_console_logging:
        logger.add(
            sys.stderr,
            level=console_log_level,
            format=CONSOLE_LOG_FORMAT,
            backtrace=True,
            diagnose=True,
        )

    if enable_file_logging:
        try:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                log_file_path,
                level=file_log_level,
                format=FILE_LOG_FORMAT,
                mode=file_mode,
                rotation=rotation,
                retention=retention,
                backtrace=True,
                diagnose=True,
            )
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")

    return logger
