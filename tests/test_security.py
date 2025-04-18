import pytest
import sys
import os
from pathlib import Path
from tidyfiles.security import SystemSecurity
from unittest.mock import patch


def test_system_path_detection_with_logging():
    """Test system path detection logs appropriate messages."""
    system_path = Path("C:/Windows" if sys.platform == "win32" else "/etc")

    is_safe, reason = SystemSecurity.is_safe_path(system_path)
    assert not is_safe
    assert "system directory" in reason


def test_safe_path_validation_with_logging(tmp_path):
    """Test path safety validation logging."""
    is_safe, reason = SystemSecurity.is_safe_path(tmp_path)
    assert is_safe
    assert reason == ""


def test_validate_path_raises_error_with_logging():
    """Test that validate_path logs errors appropriately."""
    system_path = Path("/etc" if sys.platform != "win32" else "C:/Windows")

    with pytest.raises(ValueError) as exc_info:
        SystemSecurity.validate_path(system_path)
    assert "system directory" in str(exc_info.value)


def test_non_writable_path_with_logging(tmp_path):
    """Test detection and logging of non-writable paths."""
    test_file = tmp_path / "test.txt"
    test_file.touch()

    # Make file read-only
    os.chmod(test_file, 0o444)

    try:
        is_safe, reason = SystemSecurity.is_safe_path(test_file)
        assert not is_safe
        assert "not writable" in reason
    finally:
        # Restore permissions to allow cleanup
        os.chmod(test_file, 0o644)


def test_windows_system_paths():
    """Test Windows system path detection."""
    if sys.platform == "win32":
        system_paths = SystemSecurity.get_windows_system_paths()
        assert Path("C:/Windows") in system_paths
        assert Path("C:/Program Files") in system_paths

        # Test with custom system drive
        with patch.dict(os.environ, {"SystemDrive": "D:"}):
            custom_paths = SystemSecurity.get_windows_system_paths()
            assert Path("D:/Windows") in custom_paths
            assert Path("D:/Program Files") in custom_paths


def test_macos_system_paths():
    """Test macOS system path detection."""
    if sys.platform == "darwin":
        system_paths = SystemSecurity.get_macos_system_paths()
        assert Path("/System") in system_paths
        assert Path("/Library") in system_paths
        assert Path("/.Spotlight-V100") in system_paths


def test_path_resolution_error():
    """Test handling of path resolution errors."""
    with patch("pathlib.Path.resolve", side_effect=OSError("Mock error")):
        path = Path("/some/path")
        is_system = SystemSecurity.is_system_path(path)
        assert is_system  # Should return True on error for safety


def test_macos_hidden_file_detection():
    """Test detection of macOS hidden system files."""
    if sys.platform == "darwin":
        hidden_file = Path("/some/path/._hidden")
        is_safe, reason = SystemSecurity.is_safe_path(hidden_file)
        assert not is_safe
        assert "macOS system file" in reason


def test_windows_special_file_detection():
    """Test detection of Windows special files."""
    if sys.platform == "win32":
        special_file = Path("C:/Users/test/~temp")
        is_safe, reason = SystemSecurity.is_safe_path(special_file)
        assert not is_safe
        assert "Windows special file" in reason


def test_parent_directory_permissions(tmp_path):
    """Test parent directory permission checking."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    test_file = test_dir / "test.txt"

    try:
        # Make parent directory read-only
        os.chmod(test_dir, 0o444)  # read-only for all users

        is_safe, reason = SystemSecurity.is_safe_path(test_file)
        assert not is_safe
        assert "Parent directory" in reason
        assert "not writable" in reason
    finally:
        # Restore permissions to allow cleanup
        os.chmod(test_dir, 0o755)


def test_validate_path_without_raising():
    """Test validate_path with raise_error=False."""
    system_path = Path("/etc" if sys.platform != "win32" else "C:/Windows")
    # Should not raise an exception
    SystemSecurity.validate_path(system_path, raise_error=False)


def test_path_safety_check_exception():
    """Test handling of general exceptions in path safety checking."""
    with patch.object(
        SystemSecurity, "is_system_path", side_effect=Exception("Mock error")
    ):
        is_safe, reason = SystemSecurity.is_safe_path(Path("/some/path"))
        assert not is_safe
        assert "Unable to verify path safety" in reason
