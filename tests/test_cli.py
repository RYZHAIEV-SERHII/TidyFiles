import pytest
import typer
from typer.testing import CliRunner
from tidyfiles.cli import app, version_callback, print_welcome_message

runner = CliRunner()


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
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "TidyFiles" in result.stdout


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
    assert result.exit_code != 0
    assert "Source directory does not exist" in str(result.exception)

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
    assert "DRY RUN MODE" in result.stdout

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
    assert "DRY RUN MODE" in result.stdout


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
    assert "Files transferred:" in result.stdout


def test_main_exit_case(monkeypatch):
    """Test that ctx.exit() is called when no source_dir and no version flag"""
    from tidyfiles.cli import main

    class MockContext:
        def __init__(self):
            self.called_help = False
            self.called_exit = False

        def get_help(self):
            self.called_help = True

        def exit(self):
            self.called_exit = True

    mock_ctx = MockContext()

    main(
        ctx=mock_ctx,
        source_dir=None,
        destination_dir=None,
        dry_run=False,
        unrecognized_file_name="unrecognized",
        log_console_output=True,
        log_file_output=True,
        log_console_level="INFO",
        log_file_level="INFO",
        log_file_name="test.log",
        log_folder_name=None,
        settings_file_name="settings.json",
        settings_folder_name="settings",
        version=None,
    )

    assert mock_ctx.called_help is True
    assert mock_ctx.called_exit is True
