import pytest
import shutil
from loguru import logger


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def test_logger():
    """Create a test logger."""
    # Configure a test logger
    logger.remove()  # Remove default handler
    logger.add(lambda msg: None, level="INFO")  # Add a null handler
    return logger


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    # Create test files
    (temp_dir / "document.pdf").touch()
    (temp_dir / "image.jpg").touch()
    (temp_dir / "video.mp4").touch()
    (temp_dir / "unknown.xyz").touch()

    # Create a nested directory with files
    nested_dir = temp_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "nested_doc.txt").touch()

    return temp_dir


@pytest.fixture
def clean_temp_dir(temp_dir):
    """Ensure temporary directory is clean after each test."""
    yield temp_dir
    shutil.rmtree(temp_dir)
