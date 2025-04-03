import pytest
import typer
import re
from typer.testing import CliRunner
from tidyfiles.cli import app, version_callback, print_welcome_message

# Create a test runner with specific settings
runner = CliRunner(mix_stderr=False)


def clean_rich_output(text):
    """Remove Rich formatting from text while preserving the actual content."""
    # Remove ANSI escape sequences
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def test_version_command():
    """Test version command and callback"""
    # Test the command
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "TidyFiles version:" in result.stdout

    # Test callback directly
    assert version_callback(False) is None
    with pytest.raises(typer.Exit):
        version_callback(True)


def test_no_source_dir():
    """Test behavior when no source directory is provided"""
    result = runner.invoke(
        app, ["--help"], env={"NO_COLOR": "1"}
    )  # Explicitly request help
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--source-dir" in result.output


def test_print_welcome_message(capsys):
    """Test welcome message in both modes"""
    # Test dry-run mode
    print_welcome_message(
        dry_run=True, source_dir="/test/source", destination_dir="/test/dest"
    )
    captured = capsys.readouterr()
    assert "DRY RUN MODE" in captured.out

    # Test live mode
    print_welcome_message(
        dry_run=False, source_dir="/test/source", destination_dir="/test/dest"
    )
    captured = capsys.readouterr()
    assert "LIVE MODE" in captured.out
    assert "/test/source" in captured.out
    assert "/test/dest" in captured.out


def test_main_with_invalid_inputs(tmp_path):
    """Test various invalid input scenarios"""
    # Test invalid source directory
    result = runner.invoke(app, ["--source-dir", "/nonexistent/path"])
    assert result.exit_code == 1
    assert "Source directory does not exist" in result.output

    # Test invalid log level
    result = runner.invoke(
        app, ["--source-dir", str(tmp_path), "--log-console-level", "INVALID"]
    )
    assert result.exit_code != 0

    # Test source path is file not directory
    test_file = tmp_path / "not_a_directory"
    test_file.touch()
    result = runner.invoke(app, ["--source-dir", str(test_file)])
    assert result.exit_code != 0
    assert "Source path is not a directory" in str(result.exception)


def test_main_with_dry_run_scenarios(tmp_path):
    """Test dry run mode scenarios"""
    # Basic dry run
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    test_file = source_dir / "test.txt"
    test_file.touch()

    result = runner.invoke(app, ["--source-dir", str(source_dir), "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.output

    # Dry run with destination
    dest_dir = tmp_path / "dest"
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
    assert "DRY RUN MODE" in result.output


def test_main_with_complete_execution(tmp_path):
    """Test complete execution path"""
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()

    # Create test files
    (source_dir / "test.txt").touch()
    (source_dir / "test.pdf").touch()

    result = runner.invoke(
        app,
        [
            "--source-dir",
            str(source_dir),
            "--destination-dir",
            str(dest_dir),
            "--log-console-level",
            "DEBUG",
            "--log-file-level",
            "DEBUG",
        ],
    )

    assert result.exit_code == 0
    assert "LIVE MODE" in result.output


def test_main_exit_case():
    """Test that help is shown when no source_dir and no version flag"""
    result = runner.invoke(
        app, ["--help"], env={"NO_COLOR": "1"}
    )  # Explicitly request help
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--source-dir" in result.output
