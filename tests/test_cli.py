import json
import re

import pytest
import typer
from typer.testing import CliRunner
from tidyfiles.cli import app, version_callback, print_welcome_message
from tidyfiles.history import OperationHistory

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
        app, ["--help"], env={"NO_COLOR": "1", "TERM": "dumb"}
    )  # Explicitly request help
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Usage:" in clean_output
    assert "--source-dir" in clean_output


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


def test_history_command_empty(tmp_path):
    """Test history command with no sessions"""
    history_file = tmp_path / "history.json"
    result = runner.invoke(app, ["history", "--history-file", str(history_file)])
    assert result.exit_code == 0
    assert "No sessions in history" in clean_rich_output(result.output)


def test_history_command_invalid_session(tmp_path):
    """Test history command with non-existent session"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    history.start_session(tmp_path, tmp_path)

    result = runner.invoke(
        app, ["history", "--history-file", str(history_file), "--session", "999"]
    )
    assert result.exit_code == 0
    assert "Session 999 not found" in clean_rich_output(result.output)


def test_history_command_empty_operations(tmp_path):
    """Test history command with empty operations"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    session_id = history.start_session(tmp_path, tmp_path)

    # Manually remove operations
    history.sessions[-1]["operations"] = []
    history._save_history()

    result = runner.invoke(
        app,
        ["history", "--history-file", str(history_file), "--session", str(session_id)],
    )
    assert result.exit_code == 0
    assert "No operations in session" in clean_rich_output(result.output)


def test_history_command_invalid_operation(tmp_path):
    """Test history command with invalid operation data"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    session_id = history.start_session(tmp_path, tmp_path)

    # Manually corrupt the operations data
    history.sessions[-1]["operations"] = "not_a_list"
    history._save_history()

    result = runner.invoke(
        app,
        ["history", "--history-file", str(history_file), "--session", str(session_id)],
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "No operations in session" in clean_output


def test_history_command_with_sessions(tmp_path):
    """Test history command with multiple sessions"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test sessions
    history.start_session("/test/source1", "/test/dest1")
    history.add_operation("move", "/test/source1/file1.txt", "/test/dest1/file1.txt")
    history.start_session("/test/source2", "/test/dest2")
    history.add_operation("move", "/test/source2/file2.txt", "/test/dest2/file2.txt")

    # Test default view
    result = runner.invoke(app, ["history", "--history-file", str(history_file)])
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Operation Sessions" in clean_output

    # Test with limit
    result = runner.invoke(
        app, ["history", "--history-file", str(history_file), "--limit", "1"]
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Operation Sessions" in clean_output


def test_history_command_session_details(tmp_path):
    """Test history command showing specific session details"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create a test session
    session_id = history.start_session("/test/source", "/test/dest")
    history.add_operation("move", "/test/source/file1.txt", "/test/dest/file1.txt")
    history.add_operation("move", "/test/source/file2.txt", "/test/dest/file2.txt")

    # Test session detail view
    result = runner.invoke(
        app,
        ["history", "--history-file", str(history_file), "--session", str(session_id)],
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Session Details" in clean_output
    assert "Operations" in clean_output


def test_undo_command_empty(tmp_path):
    """Test undo command with no history"""
    history_file = tmp_path / "history.json"
    result = runner.invoke(app, ["undo", "--history-file", str(history_file)])
    assert result.exit_code == 0
    assert "No sessions in history" in clean_rich_output(result.output)


def test_undo_command_no_session_or_operation(tmp_path):
    """Test undo command with no session or operation specified"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    history.start_session(tmp_path, tmp_path)

    result = runner.invoke(app, ["undo", "--history-file", str(history_file)])
    assert result.exit_code == 0
    assert "No operations in session" in clean_rich_output(result.output)


def test_undo_command_operation_cancelled(tmp_path):
    """Test undo command with operation cancelled"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", tmp_path / "test.txt", tmp_path / "test2.txt")

    result = runner.invoke(
        app,
        [
            "undo",
            "--history-file",
            str(history_file),
            "--session",
            str(session_id),
            "--number",
            "1",
        ],
        input="n\n",
    )
    assert result.exit_code == 0
    assert "Operation cancelled" in clean_rich_output(result.output)


def test_undo_command_invalid_operation_number(tmp_path):
    """Test undo command with invalid operation number"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", tmp_path / "test.txt", tmp_path / "test2.txt")

    result = runner.invoke(
        app,
        [
            "undo",
            "--history-file",
            str(history_file),
            "--session",
            str(session_id),
            "--number",
            "999",
        ],
    )
    assert result.exit_code == 0
    assert "Invalid operation number: 999" in clean_rich_output(result.output)


def test_undo_command_failed_operation(tmp_path, monkeypatch):
    """Test undo command with operation that fails to undo"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", tmp_path / "test.txt", tmp_path / "test2.txt")

    # Mock undo_operation to return False
    def mock_undo_operation(*args, **kwargs):
        return False

    monkeypatch.setattr(OperationHistory, "undo_operation", mock_undo_operation)

    result = runner.invoke(
        app,
        [
            "undo",
            "--history-file",
            str(history_file),
            "--session",
            str(session_id),
            "--number",
            "1",
        ],
        input="y\n",
    )
    assert result.exit_code == 0
    assert "Failed to undo operation" in clean_rich_output(result.output)


def test_undo_command_failed_session(tmp_path, monkeypatch):
    """Test undo command with session operations that fail to undo"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", tmp_path / "test.txt", tmp_path / "test2.txt")

    # Mock undo_operation to return False
    def mock_undo_operation(*args, **kwargs):
        return False

    monkeypatch.setattr(OperationHistory, "undo_operation", mock_undo_operation)

    result = runner.invoke(
        app,
        ["undo", "--history-file", str(history_file), "--session", str(session_id)],
        input="y\n",
    )
    assert result.exit_code == 0
    assert "Failed to undo all operations" in clean_rich_output(result.output)


def test_undo_command_session(tmp_path):
    """Test undoing an entire session"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test session
    session_id = history.start_session("/test/source", "/test/dest")
    history.add_operation("move", "/test/source/file1.txt", "/test/dest/file1.txt")
    history.add_operation("move", "/test/source/file2.txt", "/test/dest/file2.txt")

    # Test session undo with confirmation
    result = runner.invoke(
        app,
        ["undo", "--history-file", str(history_file), "--session", str(session_id)],
        input="y\n",
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Undo Session" in clean_output


def test_undo_command_operation(tmp_path):
    """Test undoing a specific operation"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test session
    session_id = history.start_session("/test/source", "/test/dest")
    history.add_operation("move", "/test/source/file1.txt", "/test/dest/file1.txt")
    history.add_operation("move", "/test/source/file2.txt", "/test/dest/file2.txt")

    # Test operation undo with confirmation
    result = runner.invoke(
        app,
        [
            "undo",
            "--history-file",
            str(history_file),
            "--session",
            str(session_id),
            "--number",
            "1",
        ],
        input="y\n",
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Undo Operation" in clean_output


def test_undo_command_invalid_session(tmp_path):
    """Test undo command with invalid session ID"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    history.start_session("/test/source", "/test/dest")

    result = runner.invoke(
        app, ["undo", "--history-file", str(history_file), "--session", "999"]
    )
    assert result.exit_code == 0
    assert "Session 999 not found" in result.output


def test_undo_command_invalid_operation(tmp_path):
    """Test undo command with invalid operation number"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test session
    session_id = history.start_session("/test/source", "/test/dest")
    history.add_operation("move", "/test/source/file1.txt", "/test/dest/file1.txt")

    # Test invalid operation number
    result = runner.invoke(
        app,
        [
            "undo",
            "--history-file",
            str(history_file),
            "--session",
            str(session_id),
            "--number",
            "999",
        ],
        input="y\n",
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Invalid operation number" in clean_output


def test_history_command_empty_session(tmp_path):
    """Test history command with session that has no operations"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create empty session
    session_id = history.start_session("/test/source", "/test/dest")

    # Verify session state in memory
    session = next(s for s in history.sessions if s["id"] == session_id)
    print(f"\nSession in memory: {json.dumps(session, indent=2)}")
    assert session["operations"] == [], "Session should have no operations in memory"

    # Verify session state in file
    saved_data = json.loads(history_file.read_text())
    saved_session = next(s for s in saved_data if s["id"] == session_id)
    print(f"\nSession in file: {json.dumps(saved_session, indent=2)}")
    assert saved_session["operations"] == [], (
        "Session should have no operations in file"
    )

    # Test session detail view
    result = runner.invoke(
        app,
        ["history", "--history-file", str(history_file), "--session", str(session_id)],
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    print(f"\nRaw CLI output: {result.output}")
    print(f"\nCleaned CLI output: {clean_output}")

    # Create a new history instance to verify loaded state
    new_history = OperationHistory(history_file)
    loaded_session = next(s for s in new_history.sessions if s["id"] == session_id)
    print(f"\nSession after reload: {json.dumps(loaded_session, indent=2)}")

    # Verify CLI output
    assert "Operations: 0" in clean_output, "CLI should show 0 operations"
    assert "No operations in session" in clean_output, (
        "CLI should show no operations message"
    )


def test_undo_command_cancelled(tmp_path):
    """Test undo command when user cancels the operation"""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test session
    session_id = history.start_session("/test/source", "/test/dest")
    history.add_operation("move", "/test/source/file1.txt", "/test/dest/file1.txt")

    # Test session undo with cancellation
    result = runner.invoke(
        app,
        ["undo", "--history-file", str(history_file), "--session", str(session_id)],
        input="n\n",
    )
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Operation cancelled" in clean_output


def test_main_exit_case():
    """Test that help is shown when no source_dir and no version flag"""
    result = runner.invoke(
        app, ["--help"], env={"NO_COLOR": "1", "TERM": "dumb"}
    )  # Explicitly request help
    assert result.exit_code == 0
    clean_output = clean_rich_output(result.output)
    assert "Usage:" in clean_output
    assert "--source-dir" in clean_output


def test_main_with_invalid_source_dir():
    """Test main function with non-existent source directory"""
    result = runner.invoke(app, ["--source-dir", "/nonexistent/path"])
    assert result.exit_code == 1
    assert "Source directory does not exist" in clean_rich_output(result.output)
