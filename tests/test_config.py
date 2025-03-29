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
    DEFAULT_CLEANING_PLAN,
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

    # Reset the open mock before continuing
    monkeypatch.undo()

    # Test directory creation error
    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    with pytest.raises(PermissionError):
        save_settings({"test": "value"}, tmp_path / "subdir" / "settings.toml")

    # Reset the mkdir mock before continuing
    monkeypatch.undo()

    # Additional test for raw settings handling
    settings_path = tmp_path / "settings.toml"
    with patch("tidyfiles.config.DEFAULT_SETTINGS_PATH", settings_path):
        # Test with minimal raw settings
        minimal_settings = {
            "source_dir": str(tmp_path),
            "log_folder_name": None,
            "log_file_name": "test.log",
        }
        settings = get_settings(**minimal_settings)
        assert (
            settings["log_file_path"]
            == (settings["destination_dir"] / "test.log").resolve()
        )

        # Test with complete raw settings
        complete_settings = DEFAULT_SETTINGS.copy()
        complete_settings.update(
            {
                "source_dir": str(tmp_path),
                "log_folder_name": None,
                "log_file_name": "complete.log",
            }
        )
        settings = get_settings(**complete_settings)
        assert (
            settings["log_file_path"]
            == (settings["destination_dir"] / "complete.log").resolve()
        )


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


def test_get_settings_edge_cases(tmp_path):
    """Test get_settings with various edge cases"""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Test with empty cleaning plan
    settings = get_settings(
        source_dir=str(source_dir),
        cleaning_plan={},
    )
    expected_plan = {
        (settings["destination_dir"] / path).resolve(): exts
        for path, exts in DEFAULT_CLEANING_PLAN.items()
    }
    assert settings["cleaning_plan"] == expected_plan

    # Test with None cleaning plan
    settings = get_settings(
        source_dir=str(source_dir),
        cleaning_plan=None,
    )
    assert settings["cleaning_plan"] == {
        (settings["destination_dir"] / path).resolve(): exts
        for path, exts in DEFAULT_CLEANING_PLAN.items()
    }

    # Test with None destination_dir
    settings = get_settings(source_dir=str(source_dir), destination_dir=None)
    assert settings["destination_dir"] == source_dir.resolve()

    # Test with empty string destination_dir
    settings = get_settings(source_dir=str(source_dir), destination_dir="")
    assert settings["destination_dir"] == source_dir.resolve()

    # Test with None excludes
    settings = get_settings(source_dir=str(source_dir), excludes=None)
    assert isinstance(settings["excludes"], set)
    assert len(settings["excludes"]) == 2  # settings file and log file

    # Test with empty excludes list
    settings = get_settings(source_dir=str(source_dir), excludes=[])
    assert isinstance(settings["excludes"], set)
    assert len(settings["excludes"]) == 2  # settings file and log file

    # Test with None log_folder_name
    settings = get_settings(
        source_dir=str(source_dir), log_folder_name=None, log_file_name="test.log"
    )
    assert (
        settings["log_file_path"]
        == (settings["destination_dir"] / "test.log").resolve()
    )

    # Test with empty string log_folder_name
    settings = get_settings(
        source_dir=str(source_dir), log_folder_name="", log_file_name="test.log"
    )
    assert (
        settings["log_file_path"]
        == (settings["destination_dir"] / "test.log").resolve()
    )

    # Test with custom log_folder_name
    custom_log_folder = str(tmp_path / "logs")
    settings = get_settings(
        source_dir=str(source_dir),
        log_folder_name=custom_log_folder,
        log_file_name="test.log",
    )
    assert settings["log_file_path"] == Path(custom_log_folder, "test.log").resolve()


def test_log_file_path_handling(tmp_path):
    """Test specific log file path handling scenarios"""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Test case 1: Explicit None for log_folder_name
    settings = get_settings(
        source_dir=str(source_dir), log_folder_name=None, log_file_name="test1.log"
    )
    assert (
        settings["log_file_path"]
        == (settings["destination_dir"] / "test1.log").resolve()
    )

    # Test case 2: Empty string for log_folder_name
    settings = get_settings(
        source_dir=str(source_dir), log_folder_name="", log_file_name="test2.log"
    )
    assert (
        settings["log_file_path"]
        == (settings["destination_dir"] / "test2.log").resolve()
    )

    # Test case 3: False-like value for log_folder_name
    settings = get_settings(
        source_dir=str(source_dir), log_folder_name="0", log_file_name="test3.log"
    )
    assert settings["log_file_path"] == Path("0").resolve() / "test3.log"

    # Test case 4: Custom log folder with absolute path
    custom_log_folder = tmp_path / "custom_logs"
    settings = get_settings(
        source_dir=str(source_dir),
        log_folder_name=str(custom_log_folder),
        log_file_name="test4.log",
    )
    assert settings["log_file_path"] == (custom_log_folder / "test4.log").resolve()

    # Test case 5: Custom log folder with relative path
    settings = get_settings(
        source_dir=str(source_dir),
        log_folder_name="./relative_logs",
        log_file_name="test5.log",
    )
    expected_path = Path("./relative_logs").resolve() / "test5.log"
    assert settings["log_file_path"] == expected_path

    # Test case 6: Default behavior without specifying log_folder_name
    settings = get_settings(source_dir=str(source_dir))
    assert (
        settings["log_file_path"]
        == (
            Path(DEFAULT_SETTINGS["log_folder_name"])
            / DEFAULT_SETTINGS["log_file_name"]
        ).resolve()
    )

    # Test case 7: Using raw_settings directly
    raw_settings = {
        "source_dir": str(source_dir),
        "destination_dir": str(source_dir),
        "log_folder_name": None,
        "log_file_name": "direct.log",
        "cleaning_plan": None,
        "unrecognized_file_name": "other",
        "log_console_output_status": True,
        "log_file_output_status": True,
        "log_console_level": "WARNING",
        "log_file_level": "DEBUG",
        "log_file_mode": "w",
        "settings_file_name": "settings.toml",
        "settings_folder_name": str(tmp_path / ".tidyfiles"),
        "excludes": [],
    }
    settings = get_settings(**raw_settings)
    assert (
        settings["log_file_path"]
        == (Path(DEFAULT_SETTINGS["log_folder_name"]) / "direct.log").resolve()
    )
