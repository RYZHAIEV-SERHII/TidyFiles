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
        get_settings(source_dir=None)  # type: ignore
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
        excludes=[str("/tmp/exclude")],  # Convert to list of strings
    )
    assert settings["log_console_level"] == "DEBUG"

    # Test with None settings_folder_name
    settings_none = get_settings(
        source_dir=str(source_dir),
        settings_folder_name="",
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


def test_get_settings_with_empty_strings(tmp_path):
    """Test get_settings with empty strings in settings."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Test with empty strings
    settings = get_settings(
        source_dir=str(source_dir),
        settings_folder_name=str(tmp_path / "config"),  # Use tmp_path instead of root
        settings_file_name="test.toml",
        log_folder_name=str(tmp_path / "logs"),  # Use tmp_path instead of root
        log_file_name="test.log",
        destination_dir="",
    )

    # Verify paths are resolved correctly
    assert settings["settings_file_path"].name == "test.toml"
    assert settings["settings_file_path"].parent == tmp_path / "config"
    assert settings["log_file_path"].name == "test.log"
    assert settings["log_file_path"].parent == tmp_path / "logs"
    assert settings["destination_dir"] == source_dir  # Should fall back to source_dir


def test_load_settings_with_nonexistent_path(tmp_path):
    """Test load_settings with a path that doesn't exist."""
    nonexistent_path = tmp_path / "nonexistent" / "settings.toml"
    settings = load_settings(nonexistent_path)
    assert settings == DEFAULT_SETTINGS
    assert nonexistent_path.exists()
    assert nonexistent_path.parent.exists()


def test_save_settings_with_write_error(tmp_path, monkeypatch):
    """Test save_settings with write errors."""
    settings_path = tmp_path / "settings.toml"

    def mock_write(*args, **kwargs):
        raise OSError("Write error")

    # Mock the write method to raise an error
    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: type(
            "MockFile",
            (),
            {
                "write": mock_write,
                "__enter__": lambda x: x,
                "__exit__": lambda *args: None,
            },
        )(),
    )

    with pytest.raises(OSError):
        save_settings({"test": "value"}, settings_path)


def test_get_settings_with_none_values(tmp_path):
    """Test get_settings with None values for optional parameters."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Test with None values for optional parameters
    settings = get_settings(
        source_dir=str(source_dir),
        destination_dir=None,  # Changed back to None
        cleaning_plan=None,
        settings_folder_name=str(tmp_path / "config"),
        log_folder_name=str(tmp_path / "logs"),
        excludes=None,
    )

    # Verify defaults are used
    assert str(settings["destination_dir"]) == str(
        source_dir
    )  # Convert both to str for comparison
    assert settings["cleaning_plan"]  # Should use DEFAULT_CLEANING_PLAN
    assert settings["settings_file_path"].exists()
    assert settings["settings_file_path"].parent == tmp_path / "config"
    assert settings["log_file_path"].parent == tmp_path / "logs"


def test_get_settings_with_empty_values(tmp_path):
    """Test get_settings with empty values."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Test with empty values
    settings = get_settings(
        source_dir=str(source_dir),
        destination_dir="",
        cleaning_plan={},
        settings_folder_name=str(tmp_path / "config"),  # Use tmp_path instead of root
        log_folder_name=str(tmp_path / "logs"),  # Use tmp_path instead of root
        excludes=[],
    )

    # Verify empty values are handled correctly
    assert settings["destination_dir"] == source_dir
    assert settings["cleaning_plan"]  # Should use DEFAULT_CLEANING_PLAN
    assert settings["settings_file_path"].is_absolute()
    assert settings["settings_file_path"].parent == tmp_path / "config"
    assert settings["log_file_path"].is_absolute()
    assert settings["log_file_path"].parent == tmp_path / "logs"
    assert isinstance(settings["excludes"], set)
    assert len(settings["excludes"]) >= 2  # Should include settings and log files


def test_get_settings_log_folder_handling(tmp_path):
    """Test get_settings log folder name handling."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create mock settings with the test path
    mock_default_settings = DEFAULT_SETTINGS.copy()
    mock_default_settings["log_folder_name"] = str(tmp_path / ".tidyfiles")

    # Create the patch context for both home and DEFAULT_SETTINGS
    with patch("pathlib.Path.home", return_value=tmp_path), patch(
        "tidyfiles.config.DEFAULT_SETTINGS", mock_default_settings
    ), patch.dict(
        "tidyfiles.config.DEFAULT_SETTINGS", mock_default_settings, clear=True
    ):
        # Test with default log folder
        settings_default_log_folder = get_settings(
            source_dir=str(source_dir),
            log_file_name="test.log",
            settings_folder_name=str(tmp_path / "config"),
            log_folder_name=str(
                tmp_path / ".tidyfiles"
            ),  # Explicitly set to match mock
        )
        # Should use default .tidyfiles directory
        assert (
            settings_default_log_folder["log_file_path"].parent
            == tmp_path / ".tidyfiles"
        )
        assert settings_default_log_folder["log_file_path"].name == "test.log"

        # Test with empty string for log folder (should use default)
        settings_empty_log_folder = get_settings(
            source_dir=str(source_dir),
            log_folder_name="",  # Empty string should fall back to default
            log_file_name="test.log",
            settings_folder_name=str(tmp_path / "config"),
        )
        assert (
            settings_empty_log_folder["log_file_path"].parent == tmp_path / ".tidyfiles"
        )
        assert settings_empty_log_folder["log_file_path"].name == "test.log"

        # Test with specific log folder
        log_folder = tmp_path / "logs"
        settings_with_log_folder = get_settings(
            source_dir=str(source_dir),
            log_folder_name=str(log_folder),
            log_file_name="test.log",
            settings_folder_name=str(tmp_path / "config"),
        )
        assert settings_with_log_folder["log_file_path"].parent == log_folder
        assert settings_with_log_folder["log_file_path"].name == "test.log"
