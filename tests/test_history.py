import json
from datetime import datetime
from pathlib import Path

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
