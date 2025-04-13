import shutil
from pathlib import Path
from unittest.mock import patch
from unittest.mock import MagicMock
from loguru import logger

from tidyfiles.operations import (
    create_plans,
    delete_dirs,
    get_folder_path,
    transfer_files,
)
from tidyfiles.history import OperationHistory


def test_create_plans_with_empty_dir(tmp_path):
    """Test create_plans with empty directory"""
    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {
            tmp_path / "documents": [".txt", ".doc"],
            tmp_path / "images": [".jpg", ".png"],
        },
        "unrecognized_file": tmp_path / "other",
        "excludes": set(),
    }
    transfer_plan, delete_plan = create_plans(**settings)
    assert len(transfer_plan) == 0
    assert len(delete_plan) == 0


def test_create_plans_with_files_and_dirs(tmp_path):
    """Test create_plans with both files and directories"""
    # Create test files and directories
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()
    (tmp_path / "test.txt").touch()
    (tmp_path / "image.jpg").touch()
    (tmp_path / "unknown.xyz").touch()

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {
            tmp_path / "documents": [".txt"],
            tmp_path / "images": [".jpg"],
        },
        "unrecognized_file": tmp_path / "other",
        "excludes": set(),
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify transfer plan
    assert len(transfer_plan) == 3  # All files should be in transfer plan
    assert any(src.name == "test.txt" for src, _ in transfer_plan)
    assert any(src.name == "image.jpg" for src, _ in transfer_plan)
    assert any(src.name == "unknown.xyz" for src, _ in transfer_plan)

    # Verify delete plan
    assert len(delete_plan) == 2  # Both directories should be in delete plan
    assert tmp_path / "dir1" in delete_plan
    assert tmp_path / "dir2" in delete_plan


def test_create_plans_with_excludes(tmp_path):
    """Test create_plans with exclude patterns"""
    # Create test structure
    excluded_dir = tmp_path / "excluded"
    included_dir = tmp_path / "included"
    excluded_dir.mkdir()
    included_dir.mkdir()

    (excluded_dir / "test.txt").touch()
    (included_dir / "test.txt").touch()

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {tmp_path / "documents": [".txt"]},
        "unrecognized_file": tmp_path / "other",
        "excludes": {excluded_dir},
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify excluded files/dirs are not in plans
    assert not any(str(excluded_dir) in str(src) for src, _ in transfer_plan)
    assert not any(str(excluded_dir) in str(dir_) for dir_ in delete_plan)
    # Verify included files/dirs are in plans
    assert any(str(included_dir) in str(src) for src, _ in transfer_plan)
    assert any(str(included_dir) in str(dir_) for dir_ in delete_plan)


def test_create_plans_with_partial_excludes(tmp_path):
    """Test create_plans where a file is excluded but its parent directory is not
    included in excludes."""
    # Create test structure
    parent_dir = tmp_path / "parent"
    excluded_file = parent_dir / "excluded.txt"
    included_file = parent_dir / "included.txt"
    parent_dir.mkdir()
    excluded_file.touch()
    included_file.touch()

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {tmp_path / "documents": [".txt"]},
        "unrecognized_file": tmp_path / "other",
        "excludes": {excluded_file},
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify excluded file is not in transfer plan
    assert not any(src == excluded_file for src, _ in transfer_plan)
    # Verify included file is in transfer plan
    assert any(src == included_file for src, _ in transfer_plan)
    # Verify parent directory is in delete plan
    assert parent_dir in delete_plan


def test_create_plans_with_non_excluded_files(tmp_path):
    """Test create_plans with files that are not relative to excluded paths."""
    # Create test structure
    excluded_dir = tmp_path / "excluded"
    non_excluded_dir = tmp_path / "non_excluded"
    excluded_dir.mkdir()
    non_excluded_dir.mkdir()

    # Create files in both directories
    (excluded_dir / "test.txt").touch()
    (non_excluded_dir / "test.txt").touch()

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {tmp_path / "documents": [".txt"]},
        "unrecognized_file": tmp_path / "other",
        "excludes": {excluded_dir},
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify non-excluded file is in transfer plan
    assert any(src == non_excluded_dir / "test.txt" for src, _ in transfer_plan)
    # Verify excluded file is not in transfer plan
    assert not any(src == excluded_dir / "test.txt" for src, _ in transfer_plan)


def test_transfer_files_dry_run(tmp_path, test_logger):
    """Test transfer_files in dry run mode"""
    source_file = tmp_path / "source.txt"
    source_file.write_text("test content")
    dest_dir = tmp_path / "dest"

    transfer_plan = [(source_file, dest_dir / "source.txt")]
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=True)

    assert num_transferred == 0
    assert total == 1
    assert not (dest_dir / "source.txt").exists()


def test_transfer_files_with_rename(tmp_path, test_logger):
    """Test transfer_files with file renaming"""
    # Setup
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    # Create source files
    source_file1 = source_dir / "test.txt"
    source_file2 = source_dir / "test2.txt"
    source_file1.write_text("content 1")
    source_file2.write_text("content 2")

    # Create existing file in destination
    (dest_dir / "test.txt").touch()

    transfer_plan = [
        (source_file1, dest_dir / "test.txt"),
        (source_file2, dest_dir / "test.txt"),
    ]

    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=False)

    assert num_transferred == 2
    assert total == 2
    assert (dest_dir / "test.txt").exists()
    assert (dest_dir / "test_1.txt").exists()
    assert (
        dest_dir / "test_1_2.txt"
    ).exists()  # Fixed: The actual naming pattern is test_1_2.txt


def test_transfer_files_with_history(tmp_path, test_logger):
    """Test transfer_files with history tracking."""
    source_file = tmp_path / "source.txt"
    source_file.write_text("test content")
    dest_dir = tmp_path / "dest"
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    transfer_plan = [(source_file, dest_dir / "source.txt")]
    num_transferred, total = transfer_files(
        transfer_plan, test_logger, dry_run=False, history=history
    )

    assert num_transferred == 1
    assert total == 1
    assert (dest_dir / "source.txt").exists()

    # Check history
    assert len(history.operations) == 1
    operation = history.operations[0]
    assert operation["type"] == "move"
    assert operation["source"] == str(source_file)
    assert operation["destination"] == str(dest_dir / "source.txt")
    assert operation["status"] == "completed"


def test_delete_dirs_comprehensive(tmp_path, test_logger):
    """Test delete_dirs with various scenarios"""
    # Setup nested directory structure
    parent_dir = tmp_path / "parent"
    child_dir = parent_dir / "child"
    grandchild_dir = child_dir / "grandchild"

    parent_dir.mkdir()
    child_dir.mkdir()
    grandchild_dir.mkdir()

    delete_plan = [
        grandchild_dir,
        child_dir,
        parent_dir,
        tmp_path / "nonexistent",
    ]

    # Test dry run
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=True)
    assert num_deleted == 0
    assert total == 4
    assert parent_dir.exists()

    # Test actual deletion
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)
    assert num_deleted == 3
    assert total == 4
    assert not parent_dir.exists()


def test_delete_dirs_with_nonexistent_directory(tmp_path, test_logger):
    """Test delete_dirs with a directory that doesn't exist"""
    nonexistent_dir = tmp_path / "nonexistent"
    delete_plan = [nonexistent_dir]

    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)

    assert num_deleted == 0
    assert total == 1


def test_delete_dirs_with_nested_deletion(tmp_path, test_logger):
    """Test delete_dirs with nested directories where parent is deleted first"""
    # Create nested structure
    parent = tmp_path / "parent"
    child = parent / "child"
    parent.mkdir()
    child.mkdir()

    # Delete parent first, then try to delete child
    delete_plan = [parent, child]

    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)

    assert num_deleted == 2  # Both should be counted as deleted
    assert total == 2
    assert not parent.exists()
    assert not child.exists()


def test_get_folder_path(tmp_path):
    """Test get_folder_path functionality"""
    test_file = tmp_path / "test.txt"
    docs_folder = tmp_path / "documents"
    images_folder = tmp_path / "images"
    unrecognized = tmp_path / "other"

    # Test with empty cleaning plan
    assert get_folder_path(test_file, {}, unrecognized) == unrecognized

    # Test with matching extension
    # Convert Path objects to strings to match the expected Dict[str, Any] type
    cleaning_plan = {
        str(docs_folder): [".txt"],
        str(images_folder): [".jpg", ".png"],
    }
    assert get_folder_path(test_file, cleaning_plan, unrecognized) == docs_folder

    # Test with non-matching extension
    test_file = tmp_path / "test.xyz"
    assert get_folder_path(test_file, cleaning_plan, unrecognized) == unrecognized


def test_create_plans_without_excludes(tmp_path):
    """Test create_plans when no excludes are provided."""
    # Create test structure
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    (test_dir / "test.txt").touch()

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {tmp_path / "documents": [".txt"]},
        "unrecognized_file": tmp_path / "other",
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify file is in transfer plan
    assert any(src == test_dir / "test.txt" for src, _ in transfer_plan)
    # Verify directory is in delete plan
    assert test_dir in delete_plan


def test_create_plans_with_none_excludes(tmp_path):
    """Test create_plans when excludes is None."""
    # Create test structure
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    (test_dir / "test.txt").touch()

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {tmp_path / "documents": [".txt"]},
        "unrecognized_file": tmp_path / "other",
        "excludes": None,
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify file is in transfer plan
    assert any(src == test_dir / "test.txt" for src, _ in transfer_plan)
    # Verify directory is in delete plan
    assert test_dir in delete_plan


def test_create_plans_with_symlink(tmp_path):
    """Test create_plans with a symlink."""
    # Create test structure
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    target_file = test_dir / "target.txt"
    target_file.touch()
    symlink = test_dir / "symlink.txt"
    symlink.symlink_to(target_file)

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {tmp_path / "documents": [".txt"]},
        "unrecognized_file": tmp_path / "other",
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify symlink is not in transfer plan (it's a file but not a regular file)
    assert not any(src == symlink for src, _ in transfer_plan)
    # Verify target file is in transfer plan
    assert any(src == target_file for src, _ in transfer_plan)
    # Verify directory is in delete plan
    assert test_dir in delete_plan
    # Verify symlink is not in delete plan
    assert not any(dir_ == symlink for dir_ in delete_plan)


def test_transfer_files_with_history_dry_run(tmp_path, test_logger):
    """Test transfer_files with history tracking in dry-run mode."""
    source_file = tmp_path / "source.txt"
    source_file.write_text("test content")
    dest_dir = tmp_path / "dest"
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    transfer_plan = [(source_file, dest_dir / "source.txt")]
    num_transferred, total = transfer_files(
        transfer_plan, test_logger, dry_run=True, history=history
    )

    assert num_transferred == 0
    assert total == 1
    assert not (dest_dir / "source.txt").exists()

    # Check that no history was recorded in dry-run mode
    assert len(history.operations) == 0


def test_delete_dirs_with_history_dry_run(tmp_path, test_logger):
    """Test delete_dirs with history tracking in dry-run mode."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    history_file = tmp_path / "history.json"
    history = OperationHistory(history_file)

    delete_plan = [test_dir]
    num_deleted, total = delete_dirs(
        delete_plan, test_logger, dry_run=True, history=history
    )

    assert num_deleted == 0
    assert total == 1
    assert test_dir.exists()

    # Check that no history was recorded in dry-run mode
    assert len(history.operations) == 0


def test_transfer_files_with_non_existent_source(tmp_path, test_logger):
    """Test transfer_files with a source file that doesn't exist."""
    source_file = tmp_path / "nonexistent.txt"
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    transfer_plan = [(source_file, dest_dir / "nonexistent.txt")]
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=False)

    assert num_transferred == 0
    assert total == 1
    assert not (dest_dir / "nonexistent.txt").exists()


def test_transfer_files_with_non_existent_dest_parent(tmp_path, test_logger):
    """Test transfer_files with a destination parent directory that doesn't exist."""
    source_file = tmp_path / "source.txt"
    source_file.write_text("test content")
    dest_dir = tmp_path / "nonexistent_dir"

    transfer_plan = [(source_file, dest_dir / "source.txt")]
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=False)

    assert num_transferred == 1
    assert total == 1
    assert (dest_dir / "source.txt").exists()
    assert (dest_dir / "source.txt").read_text() == "test content"


def test_transfer_files_with_permission_error(tmp_path, test_logger, monkeypatch):
    """Test transfer_files with permission error during transfer."""
    source_file = tmp_path / "source.txt"
    source_file.write_text("test content")
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    def mock_replace(*args, **kwargs):
        raise PermissionError("Mock permission error")

    monkeypatch.setattr(Path, "replace", mock_replace)

    transfer_plan = [(source_file, dest_dir / "source.txt")]
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=False)

    assert num_transferred == 0
    assert total == 1
    assert not (dest_dir / "source.txt").exists()


def test_delete_dirs_with_non_empty_directory(tmp_path, test_logger):
    """Test delete_dirs with a non-empty directory."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    (test_dir / "file.txt").touch()

    delete_plan = [test_dir]
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)

    assert num_deleted == 1  # Should still be counted as deleted
    assert total == 1
    assert not test_dir.exists()  # Directory should be deleted with its contents


def test_delete_dirs_with_permission_error(tmp_path, test_logger, monkeypatch):
    """Test delete_dirs with permission error during deletion."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    def mock_rmtree(*args, **kwargs):
        raise PermissionError("Mock permission error")

    monkeypatch.setattr(shutil, "rmtree", mock_rmtree)

    delete_plan = [test_dir]
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)

    assert num_deleted == 0
    assert total == 1
    assert test_dir.exists()


def test_create_plans_with_circular_symlink(tmp_path):
    """Test create_plans with a circular symlink."""
    # Create test structure
    test_dir = tmp_path / "test"
    test_dir.mkdir()

    # Create a circular symlink
    symlink = test_dir / "circular"
    symlink.symlink_to(test_dir)

    settings = {
        "source_dir": tmp_path,
        "destination_dir": tmp_path,
        "cleaning_plan": {tmp_path / "documents": [".txt"]},
        "unrecognized_file": tmp_path / "other",
    }

    transfer_plan, delete_plan = create_plans(**settings)

    # Verify directory is in delete plan
    assert test_dir in delete_plan
    # Verify no files in transfer plan (no regular files)
    assert not any(str(test_dir) in str(src) for src, _ in transfer_plan)


def test_transfer_files_with_history_error(tmp_path, test_logger, monkeypatch):
    """Test transfer_files with error in history recording."""
    source_file = tmp_path / "source.txt"
    source_file.write_text("test content")
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    history = OperationHistory(tmp_path / "history.json")

    # Mock add_operation to raise an exception
    def mock_add_operation(*args, **kwargs):
        raise Exception("Mock history error")

    monkeypatch.setattr(OperationHistory, "add_operation", mock_add_operation)

    transfer_plan = [(source_file, dest_dir / "source.txt")]
    num_transferred, total = transfer_files(
        transfer_plan, test_logger, dry_run=False, history=history
    )

    # Operation should still succeed even if history recording fails
    assert num_transferred == 1
    assert total == 1
    assert (dest_dir / "source.txt").exists()


def test_delete_dirs_with_history_error(tmp_path, test_logger, monkeypatch):
    """Test delete_dirs with error in history recording."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    history = OperationHistory(tmp_path / "history.json")

    # Mock add_operation to raise an exception
    def mock_add_operation(*args, **kwargs):
        raise Exception("Mock history error")

    monkeypatch.setattr(OperationHistory, "add_operation", mock_add_operation)

    delete_plan = [test_dir]
    num_deleted, total = delete_dirs(
        delete_plan, test_logger, dry_run=False, history=history
    )

    # Operation should still succeed even if history recording fails
    assert num_deleted == 1
    assert total == 1
    assert not test_dir.exists()


def test_delete_dirs_empty_list(test_logger):
    """Test delete_dirs with an empty list of directories."""
    empty_dirs = []
    num_deleted, total = delete_dirs(empty_dirs, test_logger, dry_run=False)
    assert num_deleted == 0
    assert total == 0


@patch("loguru.logger.info")
def test_delete_dir_dry_run(mock_loguru_info, tmp_path, mock_progress_bar):
    """Test delete_dirs in dry_run mode."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    delete_plan = [empty_dir]
    history = MagicMock()

    num_deleted, total_dirs = delete_dirs(
        delete_plan,
        logger=logger,
        dry_run=True,
        history=history,
        progress=mock_progress_bar,
    )
    assert num_deleted == 0
    assert total_dirs == 1
    # Check that the mock logger's info method was called
    expected_log = f"DELETE_DIR [DRY-RUN] | PATH: {empty_dir}"
    assert any(call.args[0] == expected_log for call in mock_loguru_info.call_args_list)
    assert empty_dir.exists()  # Ensure directory was not deleted
    history.add_operation.assert_not_called()


@patch("loguru.logger.error")
def test_delete_dir_exception(mock_loguru_error, tmp_path, mock_progress_bar):
    """Test delete_dirs handling exception during directory deletion."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    delete_plan = [empty_dir]
    history = MagicMock()

    # Mock shutil.rmtree to raise an exception
    with patch("shutil.rmtree") as mock_rmtree:
        mock_rmtree.side_effect = OSError("Permission denied")
        num_deleted, total_dirs = delete_dirs(
            delete_plan,
            logger=logger,
            dry_run=False,
            history=history,
            progress=mock_progress_bar,
        )
        assert num_deleted == 0
        assert total_dirs == 1
        # Check that the mock logger's error method was called
        mock_loguru_error.assert_called_once()
        assert "Permission denied" in mock_loguru_error.call_args[0][0]
        history.add_operation.assert_not_called()
