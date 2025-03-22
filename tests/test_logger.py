import pytest
from tidyfiles.logger import get_logger
from loguru import logger
from pathlib import Path


@pytest.fixture(autouse=True)
def setup_logger():
    # Remove all handlers before each test
    logger.remove()
    yield
    # Cleanup after test
    logger.remove()


def test_get_logger_console_only(tmp_path):
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        log_console_output_status=True,
        log_file_output_status=False,
        log_console_level="DEBUG",
        log_file_level="INFO",
        log_file_mode="w",
    )
    assert logger_instance is not None


def test_get_logger_file_only(tmp_path):
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        log_console_output_status=False,
        log_file_output_status=True,
        log_console_level="DEBUG",
        log_file_level="INFO",
        log_file_mode="w",
    )
    assert logger_instance is not None
    assert log_file.exists()


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
            log_file_path=log_file, log_console_level="INVALID", log_file_level="INFO"
        )


def test_get_logger_no_outputs(tmp_path):
    log_file = tmp_path / "test.log"
    logger_instance = get_logger(
        log_file_path=log_file,
        log_console_output_status=False,
        log_file_output_status=False,
        log_console_level="INFO",
        log_file_level="INFO",
        log_file_mode="w",
    )
    assert logger_instance is None  # Changed assertion
    assert not log_file.exists()


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


def test_get_logger_with_invalid_configuration(tmp_path):
    """Test logger with invalid configuration"""
    log_file = tmp_path / "test.log"
    # Test with at least one output enabled
    logger_instance = get_logger(
        log_file_path=log_file,
        log_console_output_status=True,
        log_file_output_status=False,
    )
    assert logger_instance is not None

    # Test with both outputs disabled
    logger_instance = get_logger(
        log_file_path=log_file,
        log_console_output_status=False,
        log_file_output_status=False,
    )
    assert logger_instance is None


def test_logger_with_invalid_file_path(tmp_path):
    # Test when log_file_path is a directory
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    with pytest.raises(ValueError, match="must be a file path, not a directory"):
        get_logger(log_file_path=log_dir, log_file_output_status=True)
