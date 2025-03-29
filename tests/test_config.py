import os
import pytest
import toml
from pathlib import Path
from unittest.mock import patch
from tidyfiles.config import (
    get_settings,
    save_settings,
    load_settings,
    DEFAULT_SETTINGS,
)


def test_get_settings_custom_configuration(tmp_path):
    """Test get_settings with custom configurations"""
    # Test custom cleaning plan
    custom_plan = {"custom": [".xyz", ".abc"], "special": [".spec"]}
    settings = get_settings(source_dir=str(tmp_path), cleaning_plan=custom_plan)
    assert "custom" in str(list(settings["cleaning_plan"].keys())[0])
    assert "special" in str(list(settings["cleaning_plan"].keys())[1])

    # Test excludes
    excludes = [".git", "node_modules"]
    settings = get_settings(source_dir=str(tmp_path), excludes=excludes)
    assert len(settings["excludes"]) >= len(excludes)
    for exclude in excludes:
        assert any(exclude in str(path) for path in settings["excludes"])


def test_get_settings_validation(tmp_path):
    """Test get_settings input validation"""
    # Test invalid source directory scenarios
    with pytest.raises(ValueError):
        get_settings(source_dir=None)
    with pytest.raises(ValueError):
        get_settings(source_dir="")
    with pytest.raises(FileNotFoundError):
        get_settings(source_dir="/nonexistent/path")

    # Test file as source instead of directory
    source_file = tmp_path / "file.txt"
    source_file.touch()
    with pytest.raises(ValueError) as exc_info:
        get_settings(source_dir=str(source_file))
    assert "not a directory" in str(exc_info.value)


def test_get_settings_comprehensive(tmp_path):
    """Test get_settings comprehensively"""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Test with all parameters
    settings = get_settings(
        source_dir=str(source_dir),
        destination_dir=str(source_dir / "dest"),
        cleaning_plan={"documents": [".txt"]},
        unrecognized_file_name="unknown",
        log_console_output_status=True,
        log_file_output_status=True,
        log_console_level="DEBUG",
        log_file_level="INFO",
        log_file_name="test.log",
        log_folder_name=str(source_dir / "logs"),
        log_file_mode="w",
        settings_file_name="settings.toml",
        settings_folder_name=str(source_dir / "config"),
        excludes=["/tmp/exclude"],
    )
    assert settings["log_console_level"] == "DEBUG"

    # Test with None settings_folder_name
    settings_none = get_settings(
        source_dir=str(source_dir),
        settings_folder_name=None,
        settings_file_name="test_settings.toml",
    )
    assert settings_none["settings_file_path"].name == "test_settings.toml"
    assert settings_none["settings_file_path"].is_absolute()


def test_settings_file_operations_and_errors(tmp_path, monkeypatch):
    """Test settings file operations and error handling"""
    # Basic save and load
    settings = {"test_key": "test_value"}
    settings_path = tmp_path / "settings.toml"
    save_settings(settings, settings_path)
    assert settings_path.exists()
    loaded_settings = load_settings(settings_path)
    assert loaded_settings["test_key"] == "test_value"

    # Test None path - should use mocked DEFAULT_SETTINGS_PATH
    mock_default_path = tmp_path / "default_settings.toml"
    monkeypatch.setattr("tidyfiles.config.DEFAULT_SETTINGS_PATH", mock_default_path)

    test_settings = {"test": "value"}
    save_settings(test_settings, None)
    loaded = load_settings(None)
    assert loaded["test"] == "value"
    assert mock_default_path.exists()

    # Test invalid TOML
    invalid_toml = tmp_path / "invalid.toml"
    invalid_toml.write_text("invalid [ toml content")
    with pytest.raises(RuntimeError) as exc_info:
        load_settings(invalid_toml)
    assert "Failed to load settings" in str(exc_info.value)

    # Test permission errors
    settings_file = tmp_path / "no_access.toml"
    settings_file.write_text("valid = true")
    os.chmod(settings_file, 0o000)
    try:
        with pytest.raises(RuntimeError):
            load_settings(settings_file)
    finally:
        os.chmod(settings_file, 0o666)

    def mock_open_error(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open_error)
    with pytest.raises(PermissionError):
        save_settings({"test": "value"}, tmp_path / "settings.toml")

    # Test directory creation error
    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    with pytest.raises(PermissionError):
        save_settings({"test": "value"}, tmp_path / "subdir" / "settings.toml")


def test_load_settings_none_path(temp_dir):
    """Test load_settings with None path"""
    settings_path = temp_dir / ".tidyfiles" / "settings.toml"

    with patch("tidyfiles.config.DEFAULT_SETTINGS_PATH", settings_path):
        # Test loading settings with None path - should create default settings
        loaded_settings = load_settings(None)

        # Verify that all default settings are present
        assert loaded_settings == DEFAULT_SETTINGS

        # Verify the file was created in the correct location
        assert settings_path.exists()

        # Verify the content matches DEFAULT_SETTINGS
        saved_settings = toml.loads(settings_path.read_text())
        assert saved_settings == DEFAULT_SETTINGS

        # Test loading again from the created file
        reloaded_settings = load_settings(None)
        assert reloaded_settings == DEFAULT_SETTINGS

    # Clean up
    if settings_path.exists():
        settings_path.unlink()
    if settings_path.parent.exists():
        settings_path.parent.rmdir()


def test_get_settings_destination_errors(tmp_path, monkeypatch):
    """Test get_settings destination directory error handling"""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    dest_dir = tmp_path / "dest"

    # Test file instead of directory
    dest_dir.touch()
    with pytest.raises(ValueError) as exc_info:
        get_settings(source_dir=str(source_dir), destination_dir=str(dest_dir))
    assert "not a directory" in str(exc_info.value)

    # Test permission error on destination creation
    dest_dir.unlink()

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    with pytest.raises(ValueError) as exc_info:
        get_settings(source_dir=str(source_dir), destination_dir=str(dest_dir))
    assert "Cannot create destination directory" in str(exc_info.value)
