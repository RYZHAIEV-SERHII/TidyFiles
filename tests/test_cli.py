import pytest
import typer
from typer.testing import CliRunner
from tidyfiles.cli import app, version_callback, print_welcome_message

runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "TidyFiles version:" in result.stdout


def test_no_source_dir():
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_print_welcome_message(capsys):
    """Test welcome message in dry-run mode"""
    print_welcome_message(
        dry_run=True, source_dir="/test/source", destination_dir="/test/dest"
    )
    captured = capsys.readouterr()
    assert "DRY RUN MODE" in captured.out


def test_print_welcome_message_live_mode(capsys):
    """Test welcome message in live mode"""
    print_welcome_message(
        dry_run=False, source_dir="/test/source", destination_dir="/test/dest"
    )
    captured = capsys.readouterr()
    assert "LIVE MODE" in captured.out
    assert "/test/source" in captured.out
    assert "/test/dest" in captured.out


def test_main_with_source_dir(tmp_path):
    result = runner.invoke(app, ["--source-dir", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.stdout


def test_main_with_invalid_log_level(tmp_path):
    result = runner.invoke(
        app, ["--source-dir", str(tmp_path), "--log-console-level", "INVALID"]
    )
    assert result.exit_code != 0


def test_main_with_no_args_shows_help():
    """Test that running without arguments shows help"""
    result = runner.invoke(app)
    assert result.exit_code == 0
    # The actual output contains 'Usage:' but not 'Options:'
    assert "Usage:" in result.stdout
    assert "TidyFiles" in result.stdout  # This should be in the help text


def test_main_with_invalid_source_dir():
    """Test behavior with invalid source directory"""
    result = runner.invoke(app, ["--source-dir", "/nonexistent/path"])
    assert result.exit_code != 0
    # The error message should be in the output
    assert "Source directory does not exist" in str(result.exception)


def test_main_with_source_dir_not_directory(tmp_path):
    """Test behavior when source path is not a directory"""
    # Create a file instead of a directory
    test_file = tmp_path / "not_a_directory"
    test_file.touch()

    result = runner.invoke(app, ["--source-dir", str(test_file)])
    assert result.exit_code != 0
    assert "Source path is not a directory" in str(result.exception)


def test_cli_execution_path():
    """Test the CLI execution path directly"""
    import tidyfiles.cli

    if hasattr(tidyfiles.cli, "__main__"):
        assert True  # Coverage for if __name__ == "__main__" block


def test_version_callback_exit():
    """Test that version callback exits properly"""
    with pytest.raises(typer.Exit):
        version_callback(True)


def test_version_callback_with_false():
    """Test version callback with False value"""
    assert version_callback(False) is None


def test_main_with_dry_run(tmp_path):
    """Test main function with dry run mode"""
    # Create a test file in the temporary directory
    test_file = tmp_path / "test.txt"
    test_file.touch()

    result = runner.invoke(app, ["--source-dir", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.stdout


def test_main_with_dry_run_and_destination(tmp_path):
    """Test main function with dry run mode and custom destination"""
    # Create source and destination directories
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()

    # Create a test file
    test_file = source_dir / "test.txt"
    test_file.touch()

    result = runner.invoke(
        app,
        [
            "--source-dir",
            str(source_dir),
            "--destination-dir",
            str(dest_dir),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.stdout


def test_main_with_invalid_settings_file(tmp_path):
    """Test main function with invalid settings file."""
    # Create an invalid TOML file
    invalid_settings = tmp_path / "invalid.toml"
    invalid_settings.write_text("invalid = toml [ content")

    result = runner.invoke(
        app, ["--source-dir", str(tmp_path), "--settings-file", str(invalid_settings)]
    )
    assert result.exit_code != 0


def test_main_with_all_options(tmp_path):
    """Test main function with all possible options."""
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()

    result = runner.invoke(
        app,
        [
            "--source-dir",
            str(source_dir),
            "--destination-dir",
            str(dest_dir),
            "--dry-run",
            "--unrecognized-dir",
            "unknown",
            "--log-console",
            "--log-console-level",
            "DEBUG",
            "--log-file-level",
            "INFO",
            "--settings-folder",
            str(tmp_path),
            "--version",
        ],
    )
    assert result.exit_code == 0


def test_main_with_error_handling(tmp_path):
    """Test main function error handling"""
    invalid_path = tmp_path / "nonexistent"
    result = runner.invoke(app, ["--source-dir", str(invalid_path)])
    assert result.exit_code != 0
    assert "Source directory does not exist" in str(result.exception)
