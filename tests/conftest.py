import pytest
import shutil
from loguru import logger
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    yield tmp_path
    # Ensure cleanup
    if tmp_path.exists():
        shutil.rmtree(tmp_path)


@pytest.fixture(autouse=True)
def mock_home_dir(temp_dir, monkeypatch):
    """Mock home directory to use temporary directory."""

    def mock_home():
        return Path(temp_dir)

    monkeypatch.setattr(Path, "home", mock_home)
    yield temp_dir


@pytest.fixture
def test_logger():
    """Create a test logger that doesn't write to disk."""
    logger.remove()  # Remove default handler
    test_handler_id = logger.add(lambda msg: None, level="INFO")  # Add a null handler
    yield logger
    logger.remove(test_handler_id)  # Clean up the test handler


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    # Create test files within temp_dir
    (temp_dir / "document.pdf").touch()
    (temp_dir / "image.jpg").touch()
    (temp_dir / "video.mp4").touch()
    (temp_dir / "unknown.xyz").touch()

    # Create a nested directory with files
    nested_dir = temp_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "nested_doc.txt").touch()

    yield temp_dir


@pytest.fixture(autouse=True)
def clean_temp_dir(temp_dir):
    """Automatically clean temporary directory after each test."""
    yield temp_dir
    # Clean up any files created during the test
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@contextmanager
def mock_settings_context(temp_dir):
    """Context manager to mock settings path and ensure cleanup."""
    settings_path = temp_dir / ".tidyfiles" / "settings.toml"
    with patch("tidyfiles.config.DEFAULT_SETTINGS_PATH", settings_path):
        yield settings_path
    if settings_path.exists():
        settings_path.unlink()
    if settings_path.parent.exists():
        settings_path.parent.rmdir()


@pytest.fixture(autouse=True)
def mock_settings_file(temp_dir):
    """Mock DEFAULT_SETTINGS_PATH to use temporary directory."""
    with mock_settings_context(temp_dir) as settings_path:
        yield settings_path


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """Clean up any test files after all tests are done."""
    yield
    test_settings = Path("test_settings.toml")
    if test_settings.exists():
        test_settings.unlink()
