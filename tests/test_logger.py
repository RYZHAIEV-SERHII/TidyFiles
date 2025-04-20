import pytest
from tidyfiles.logger import get_logger, LogLevel
from loguru import logger
from pathlib import Path


@pytest.fixture(autouse=True)
def setup_logger():
    logger.remove()
    yield
    logger.remove()


def test_get_logger_console_only(tmp_path):
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        enable_console_logging=True,
        enable_file_logging=False,
        console_log_level="DEBUG",
        file_log_level="INFO",
        file_mode="w",
    )
    assert logger_instance is not None
    # Test actual logging
    logger_instance.debug("Test debug message")
    logger_instance.info("Test info message")
    assert not log_file.exists()  # Verify no file was created


def test_get_logger_file_only(tmp_path):
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        enable_console_logging=False,
        enable_file_logging=True,
        console_log_level="DEBUG",
        file_log_level="INFO",
        file_mode="w",
    )
    assert logger_instance is not None
    assert log_file.exists()
    # Test actual logging
    logger_instance.info("Test info message")
    assert log_file.read_text()  # Verify message was written


def test_get_logger_both_outputs(tmp_path):
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        log_console_output_status=True,
        log_file_output_status=True,
        log_console_level="DEBUG",
        log_file_level="INFO",
        log_file_mode="a",
    )
    assert logger_instance is not None
    assert log_file.exists()


def test_get_logger_invalid_level(tmp_path):
    log_file = tmp_path / "test.log"
    with pytest.raises(ValueError):
        get_logger(
            log_file_path=log_file,
            console_log_level="INVALID",
        )


def test_get_logger_file_mkdir_error(tmp_path, monkeypatch):
    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    log_file = tmp_path / "subdir" / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        log_file_output_status=True,
    )
    assert logger_instance is not None


def test_get_logger_with_invalid_path(tmp_path):
    """Test get_logger with invalid path."""
    invalid_path = tmp_path / "nonexistent" / "log.txt"
    logger_instance = get_logger(
        log_file_path=invalid_path,
        log_console_output_status=True,
        log_file_output_status=True,
    )
    assert logger_instance is not None


def test_get_logger_with_permission_error(tmp_path, monkeypatch):
    """Test get_logger with permission error."""

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    log_path = tmp_path / "logs" / "app.log"
    logger_instance = get_logger(
        log_file_path=log_path,
        log_console_output_status=True,
        log_file_output_status=True,
    )
    assert logger_instance is not None


def test_logger_with_invalid_file_path(tmp_path):
    # Test when log_file_path is a directory
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    with pytest.raises(ValueError, match="must be a file path, not a directory"):
        get_logger(log_file_path=log_dir, log_file_output_status=True)


def test_get_logger_with_rotation(tmp_path):
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        enable_console_logging=True,
        enable_file_logging=True,
        console_log_level="DEBUG",
        file_log_level="INFO",
        file_mode="w",
        rotation="1 MB",
        retention="1 day",
    )
    assert logger_instance is not None


def test_get_logger_with_rotation_and_retention(tmp_path):
    """Test logger with rotation and retention settings."""
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        enable_console_logging=False,
        enable_file_logging=True,
        file_log_level="INFO",
        file_mode="w",
        rotation="1 MB",
        retention="1 day",
        compression="zip",
    )
    assert logger_instance is not None
    logger_instance.info("Test rotation message")
    assert log_file.exists()


def test_get_logger_file_creation_error(tmp_path, monkeypatch):
    """Test logger behavior when file creation fails."""

    def mock_add(*args, **kwargs):
        if "sink" in kwargs and isinstance(kwargs["sink"], (str, Path)):
            raise PermissionError("Failed to create log file")
        return 1  # Return a dummy handler ID for console logging

    monkeypatch.setattr(logger, "add", mock_add)

    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        enable_console_logging=True,
        enable_file_logging=True,
        console_log_level="DEBUG",
        file_log_level="INFO",
    )

    assert logger_instance is not None
    # Should still be able to log to console
    logger_instance.info("Test message")


def test_get_logger_invalid_file_mode(tmp_path):
    """Test logger with invalid file mode."""
    with pytest.raises(ValueError, match="file_mode must be 'a' or 'w'"):
        get_logger(
            log_file_path=tmp_path / "test.log",
            file_mode="x",  # Invalid mode
        )


def test_get_logger_enum_level_input(tmp_path):
    """Test logger with LogLevel enum input."""
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        console_log_level=LogLevel.DEBUG,
        file_log_level=LogLevel.INFO,
    )
    assert logger_instance is not None


def test_get_logger_string_level_input(tmp_path):
    """Test logger with string level input."""
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file, console_log_level="DEBUG", file_log_level="INFO"
    )
    assert logger_instance is not None


def test_get_logger_file_handler_error(tmp_path, monkeypatch):
    """Test logger when file handler addition fails."""

    def mock_add(*args, **kwargs):
        if isinstance(kwargs.get("sink"), Path):
            raise OSError("Failed to create log file")
        return 1  # Return handler ID for console logging

    monkeypatch.setattr(logger, "add", mock_add)

    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file, enable_console_logging=True, enable_file_logging=True
    )

    assert logger_instance is not None


def test_get_logger_mkdir_error(tmp_path, monkeypatch):
    """Test logger when directory creation fails."""

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    log_file = tmp_path / "subdir" / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file, enable_console_logging=True, enable_file_logging=True
    )

    assert logger_instance is not None


def test_get_logger_symlink_resolution(tmp_path):
    """Test logger with symlink path resolution."""
    real_log_dir = tmp_path / "real_logs"
    real_log_dir.mkdir()
    symlink_dir = tmp_path / "logs"
    symlink_dir.symlink_to(real_log_dir)

    log_file = symlink_dir / "test.log"
    logger_instance = get_logger(log_file_path=log_file, enable_file_logging=True)

    assert logger_instance is not None
    assert log_file.resolve().parent == real_log_dir


def test_get_logger_no_enabled_outputs(tmp_path):
    """Test logger with both outputs disabled."""
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file, enable_console_logging=False, enable_file_logging=False
    )
    assert logger_instance is None
