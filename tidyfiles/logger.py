import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def get_logger(
    log_file_path: Path,
    log_console_output_status: bool = True,
    log_file_output_status: bool = True,
    log_console_level: str = "WARNING",
    log_file_level: str = "INFO",
    log_file_mode: str = "a",
    **kwargs,
) -> Optional[logger]:
    """
    Creates a logger and configures it.

    Logger can output logs to console, file or both.

    Args:
        log_file_path (Path): Path to the log file.
        log_console_output_status (bool): Whether to output logs to console. Defaults to True.
        log_file_output_status (bool): Whether to output logs to file. Defaults to True.
        log_console_level (str): Logging level for console. Defaults to WARNING.
        log_file_level (str): Logging level for file. Defaults to INFO.
        log_file_mode (str): Mode for logging to file. Defaults to 'a'.
        **kwargs: Additional args for logger. Used just for simplifying settings passing.

    Returns:
        Optional[logger]: The logger instance. If not successful, None is returned.
    """
    if log_file_output_status and log_file_path.is_dir():
        raise ValueError("`log_file_path` must be a file path, not a directory.")

    if log_file_output_status or log_console_output_status:
        # configure logger
        logger.remove()  # remove default handlers

        console_log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        file_log_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        )

        if log_console_output_status:
            # create console handler
            logger.add(
                sys.stderr,
                level=log_console_level,
                format=console_log_format,
            )

        if log_file_output_status:
            # create file handler
            try:
                log_file_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create log directory: {e}")
            logger.add(
                log_file_path,
                level=log_file_level,
                format=file_log_format,
                mode=log_file_mode,
            )

        return logger
