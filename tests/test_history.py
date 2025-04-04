import json
from datetime import datetime
from pathlib import Path
import shutil

from tidyfiles.history import OperationHistory


def test_history_initialization(tmp_path):
    """Test history initialization with new file."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    assert history.operations == []
    assert history_file.exists()


def test_history_load_existing(tmp_path):
    """Test loading existing history file."""
    history_file = tmp_path / "history.json"
    test_operations = [
        {
            "type": "move",
            "source": "/test/source.txt",
            "destination": "/test/dest.txt",
            "timestamp": "2024-01-01T00:00:00",
            "status": "completed",
        }
    ]
    with open(history_file, "w") as f:
        json.dump(test_operations, f)

    history = OperationHistory(history_file)
    assert len(history.operations) == 1
    assert history.operations[0]["type"] == "move"


def test_history_add_operation(tmp_path):
    """Test adding new operation to history."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    source = Path("/test/source.txt")
    destination = Path("/test/dest.txt")
    timestamp = datetime.now()

    history.add_operation("move", source, destination, timestamp)

    assert len(history.operations) == 1
    operation = history.operations[0]
    assert operation["type"] == "move"
    assert operation["source"] == str(source)
    assert operation["destination"] == str(destination)
    assert operation["timestamp"] == timestamp.isoformat()
    assert operation["status"] == "completed"


def test_history_undo_move(tmp_path):
    """Test undoing a move operation."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test files
    source = tmp_path / "source.txt"
    destination = tmp_path / "dest.txt"
    source.write_text("test content")

    # Add move operation
    history.add_operation("move", source, destination)

    # Perform the move
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.replace(destination)

    # Undo the operation
    assert history.undo_last_operation()
    assert source.exists()
    assert not destination.exists()
    assert history.operations[0]["status"] == "undone"


def test_history_undo_delete(tmp_path):
    """Test undoing a delete operation."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Add delete operation
    history.add_operation("delete", test_dir, test_dir)

    # Perform the delete
    test_dir.rmdir()

    # Undo the operation
    assert history.undo_last_operation()
    assert test_dir.exists()
    assert history.operations[0]["status"] == "undone"


def test_history_undo_nonexistent(tmp_path):
    """Test undoing when no operations exist."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)
    assert not history.undo_last_operation()


def test_history_undo_failed_move(tmp_path, monkeypatch):
    """Test handling failed undo operation."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    source = Path("/test/source.txt")
    destination = Path("/test/dest.txt")
    history.add_operation("move", source, destination)

    # Mock shutil.move to raise an exception
    def mock_move(*args, **kwargs):
        raise OSError("Mock error")

    monkeypatch.setattr("shutil.move", mock_move)

    assert not history.undo_last_operation()


def test_history_clear(tmp_path):
    """Test clearing history."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Add some operations
    source = Path("/test/source.txt")
    destination = Path("/test/dest.txt")
    history.add_operation("move", source, destination)
    history.add_operation("delete", source, source)

    assert len(history.operations) == 2

    history.clear_history()
    assert len(history.operations) == 0


def test_history_load_invalid_json(tmp_path):
    """Test loading invalid JSON file."""
    history_file = tmp_path / "history.json"
    history_file.write_text("invalid json content")

    history = OperationHistory(history_file)
    assert history.sessions == []


def test_history_load_old_format(tmp_path):
    """Test loading history file with old format."""
    history_file = tmp_path / "history.json"
    old_format_data = [
        {"source": "/test/source.txt", "destination": "/test/dest.txt"},
        {
            "source": "/test/source2.txt",
            "destination": "/test/source2.txt",  # Same path indicates delete
        },
    ]
    history_file.write_text(json.dumps(old_format_data))

    history = OperationHistory(history_file)
    assert len(history.sessions) == 1
    assert len(history.operations) == 2
    assert history.operations[0]["type"] == "move"
    assert history.operations[1]["type"] == "delete"


def test_history_load_old_format_minimal(tmp_path):
    """Test loading old format with minimal data."""
    history_file = tmp_path / "history.json"
    old_format_data = [
        {
            # Missing most fields to test defaults
            "destination": "/test/dest.txt"
        }
    ]
    history_file.write_text(json.dumps(old_format_data))

    history = OperationHistory(history_file)
    assert len(history.sessions) == 1
    assert len(history.operations) == 1
    op = history.operations[0]
    assert op["source"] == "unknown"
    assert op["type"] == "move"
    assert op["status"] == "completed"
    assert "timestamp" in op


def test_history_load_invalid_format(tmp_path):
    """Test loading history with invalid format."""
    history_file = tmp_path / "history.json"
    invalid_data = {"not_a_list": True}
    history_file.write_text(json.dumps(invalid_data))

    history = OperationHistory(history_file)
    assert history.sessions == []


def test_history_load_invalid_data_types(tmp_path):
    """Test loading history with invalid data types."""
    history_file = tmp_path / "history.json"
    invalid_data = {
        "sessions": [
            {"not_a_session": True},  # Invalid session format
            ["not_a_dict"],  # Invalid operation format
            None,  # Invalid data type
        ]
    }
    history_file.write_text(json.dumps(invalid_data))

    history = OperationHistory(history_file)
    assert history.sessions == []


def test_history_load_missing_fields(tmp_path):
    """Test loading history with missing required fields."""
    history_file = tmp_path / "history.json"
    data_with_missing_fields = [
        {
            # Missing source
            "destination": "/test/dest.txt",
            "timestamp": "2024-01-01T00:00:00",
        }
    ]
    history_file.write_text(json.dumps(data_with_missing_fields))

    history = OperationHistory(history_file)
    assert len(history.sessions) == 1
    assert history.operations[0]["source"] == "unknown"


def test_history_save_error(tmp_path, monkeypatch):
    """Test error handling when saving history."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    def mock_open(*args, **kwargs):
        raise OSError("Mock save error")

    monkeypatch.setattr("builtins.open", mock_open)

    # Should not raise exception
    history._save_history()

    # Test saving with invalid JSON data
    history.sessions = [object()]  # Object that can't be JSON serialized
    history._save_history()  # Should handle the error gracefully


def test_history_start_session_with_active(tmp_path):
    """Test starting new session with active session."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Start first session
    session1_id = history.start_session(Path("/test/source1"), Path("/test/dest1"))
    history.add_operation("move", Path("/test/file1.txt"), Path("/test/dest/file1.txt"))

    # Start second session without completing first
    session2_id = history.start_session(Path("/test/source2"), Path("/test/dest2"))

    assert session1_id != session2_id
    assert history.sessions[-2]["status"] == "completed"


def test_history_start_session_none_paths(tmp_path):
    """Test starting session with None paths."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    history.start_session(None, None)
    assert history.sessions[-1]["source_dir"] is None
    assert history.sessions[-1]["destination_dir"] is None


def test_history_start_session_none_string_paths(tmp_path):
    """Test starting session with 'None' string paths."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    history.start_session(Path("None"), Path("None"))
    assert history.sessions[-1]["source_dir"] is None
    assert history.sessions[-1]["destination_dir"] is None


def test_history_undo_operation_specific_index(tmp_path):
    """Test undoing specific operation by index."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create test files
    source1 = tmp_path / "source1.txt"
    dest1 = tmp_path / "dest1.txt"
    source2 = tmp_path / "source2.txt"
    dest2 = tmp_path / "dest2.txt"

    source1.write_text("test1")
    source2.write_text("test2")

    # Add operations
    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", source1, dest1)
    history.add_operation("move", source2, dest2)

    # Perform moves
    shutil.move(str(source1), str(dest1))
    shutil.move(str(source2), str(dest2))

    # Undo first operation
    assert history.undo_operation(session_id, 0)
    assert source1.exists()
    assert not dest1.exists()
    assert not source2.exists()
    assert dest2.exists()

    # Try to undo invalid index
    assert not history.undo_operation(session_id, 999)


def test_history_undo_already_undone(tmp_path):
    """Test attempting to undo already undone operation."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    # Create and move test file
    source = tmp_path / "source.txt"
    dest = tmp_path / "dest.txt"
    source.write_text("test")

    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", source, dest)
    shutil.move(str(source), str(dest))

    # Undo first time
    assert history.undo_operation(session_id, 0)
    # Try to undo again
    assert not history.undo_operation(session_id, 0)


def test_history_undo_nonexistent_file(tmp_path):
    """Test undoing when destination file doesn't exist."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    source = tmp_path / "source.txt"
    dest = tmp_path / "dest.txt"

    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", source, dest)

    # Create destination directory to test mkdir error
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.parent.chmod(0o444)  # Make directory read-only

    try:
        assert not history.undo_operation(session_id, 0)
    finally:
        dest.parent.chmod(0o755)  # Restore permissions


def test_history_undo_operation_error(tmp_path, monkeypatch):
    """Test error handling during undo operation."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    source = tmp_path / "source.txt"
    dest = tmp_path / "dest.txt"
    source.write_text("test")

    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("move", source, dest)
    shutil.move(str(source), str(dest))

    def mock_move(*args, **kwargs):
        raise PermissionError("Mock permission error")

    monkeypatch.setattr("shutil.move", mock_move)

    assert not history.undo_operation(session_id, 0)


def test_history_undo_operation_invalid_type(tmp_path):
    """Test undoing operation with invalid type."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    source = tmp_path / "source.txt"
    dest = tmp_path / "dest.txt"
    source.write_text("test")
    shutil.move(str(source), str(dest))  # Actually move the file

    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("invalid_type", source, dest)

    assert not history.undo_operation(session_id, 0)
    assert dest.exists()  # File should still be at destination
    assert not source.exists()  # Source should not exist


def test_history_undo_delete_error(tmp_path, monkeypatch):
    """Test error handling during delete undo."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    test_dir = tmp_path / "test_dir"

    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("delete", test_dir, test_dir)

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Mock permission error")

    monkeypatch.setattr("pathlib.Path.mkdir", mock_mkdir)

    assert not history.undo_operation(session_id, 0)


def test_history_undo_existing_directory(tmp_path):
    """Test undoing delete when directory already exists."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    session_id = history.start_session(tmp_path, tmp_path)
    history.add_operation("delete", test_dir, test_dir)

    assert not history.undo_operation(session_id, 0)


def test_history_get_last_operation_empty(tmp_path):
    """Test getting last operation with empty history."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    assert history.get_last_operation() is None


def test_history_get_last_session_empty(tmp_path):
    """Test getting last session with empty history."""
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    assert history.get_last_session() is None
