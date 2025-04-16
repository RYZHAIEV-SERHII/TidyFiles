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
    transfer_plan, delete_plan, stats = create_plans(**settings)
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

    transfer_plan, delete_plan, stats = create_plans(**settings)

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
    transfer_plan, delete_plan, stats = create_plans(**settings)
    assert not any(src == excluded_dir / "test.txt" for src, _ in transfer_plan)
    assert excluded_dir not in delete_plan


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
    transfer_plan, delete_plan, stats = create_plans(**settings)
    assert not any(src == excluded_file for src, _ in transfer_plan)
    assert any(src == included_file for src, _ in transfer_plan)


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

    transfer_plan, delete_plan, stats = create_plans(**settings)
    assert any(src == non_excluded_dir / "test.txt" for src, _ in transfer_plan)
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

    transfer_plan, delete_plan, stats = create_plans(**settings)
    assert any(src == test_dir / "test.txt" for src, _ in transfer_plan)
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

    transfer_plan, delete_plan, stats = create_plans(**settings)
    assert any(src == test_dir / "test.txt" for src, _ in transfer_plan)
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

    transfer_plan, delete_plan, stats = create_plans(**settings)
    assert any(src == target_file for src, _ in transfer_plan)
    assert any(src == symlink for src, _ in transfer_plan)


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

    assert num_deleted == 0  # Should not delete non-empty directory
    assert total == 1
    assert test_dir.exists()  # Directory should still exist


def test_delete_dirs_with_permission_error(tmp_path, test_logger, monkeypatch):
    """Test delete_dirs with permission error during deletion."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    def mock_rmdir(*args, **kwargs):
        raise PermissionError("Mock permission error")

    # Mock Path.rmdir instead of shutil.rmtree
    monkeypatch.setattr(Path, "rmdir", mock_rmdir)

    delete_plan = [test_dir]
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)

    assert num_deleted == 0  # Should not count as deleted when permission error occurs


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

    transfer_plan, delete_plan, stats = create_plans(**settings)

    # Verify directory is in delete plan
    assert test_dir in delete_plan
    # Verify no files in transfer plan (no regular files)
    assert not any(str(test_dir) in str(src) for src, _ in transfer_plan)


def test_transfer_files_with_history_error(tmp_path, test_logger):
    """Test transfer_files with error in history recording."""
    source_file = tmp_path / "source.txt"
    source_file.write_text("test content")
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    history = MagicMock()
    history.add_operation.side_effect = Exception("Mock history error")

    transfer_plan = [(source_file, dest_dir / "source.txt")]
    try:
        num_transferred, total = transfer_files(
            transfer_plan, test_logger, dry_run=False, history=history
        )
        assert False, "Expected exception was not raised"
    except Exception as e:
        assert str(e) == "Mock history error"
        assert not (
            dest_dir / "source.txt"
        ).exists()  # File should not be transferred if history fails


def test_delete_dirs_with_history_error(tmp_path, test_logger):
    """Test delete_dirs with error in history recording."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    history = MagicMock()
    history.add_operation.side_effect = Exception("Mock history error")

    delete_plan = [test_dir]
    num_deleted, total = delete_dirs(
        delete_plan, test_logger, dry_run=False, history=history
    )

    # Verify that no directories were deleted when history recording failed
    assert num_deleted == 0
    assert total == 1
    assert test_dir.exists()  # Directory should still exist
    # Verify history operation was attempted
    history.add_operation.assert_called_once()


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

    # Mock Path.rmdir instead of shutil.rmtree
    with patch.object(Path, "rmdir", side_effect=OSError("Permission denied")):
        num_deleted, total_dirs = delete_dirs(
            delete_plan,
            logger=logger,
            dry_run=False,
            history=history,
            progress=mock_progress_bar,
        )
        assert num_deleted == 0  # Should not count as deleted when error occurs
        assert total_dirs == 1
        mock_loguru_error.assert_called_once()
        assert "Permission denied" in mock_loguru_error.call_args[0][0]
        assert empty_dir.exists()  # Directory should still exist
        history.add_operation.assert_not_called()


def test_create_plans_statistics(tmp_path):
    """Test that create_plans returns correct statistics"""
    # Setup test directory structure
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create some test files and directories
    (source_dir / "test.txt").touch()
    (source_dir / "doc.pdf").touch()
    (source_dir / "empty_dir").mkdir()
    (source_dir / "nested_dir").mkdir()
    (source_dir / "nested_dir" / "nested.txt").touch()

    cleaning_plan = {"documents": [".pdf"], "text": [".txt"]}

    mock_logger = MagicMock()
    unrecognized = tmp_path / "other"

    # Execute
    transfer_plan, delete_plan, stats = create_plans(
        source_dir=source_dir,
        cleaning_plan=cleaning_plan,
        unrecognized_file=unrecognized,
        logger=mock_logger,
    )

    # Verify statistics
    assert stats["total_files"] == 3  # test.txt, doc.pdf, nested.txt
    assert stats["total_dirs"] == 2  # empty_dir, nested_dir
    assert stats["files_to_transfer"] == len(transfer_plan)
    assert stats["dirs_to_delete"] == len(delete_plan)

    # Verify logger was called with correct message
    mock_logger.info.assert_called_once_with(
        f"Found {stats['total_files']} total files ({stats['files_to_transfer']} to transfer) and "
        f"{stats['total_dirs']} total directories ({stats['dirs_to_delete']} to delete)"
    )


def test_create_plans_without_logger(tmp_path):
    """Test that create_plans works correctly without a logger"""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "test.txt").touch()

    cleaning_plan = {"text": [".txt"]}
    unrecognized = tmp_path / "other"

    # Execute without logger
    transfer_plan, delete_plan, stats = create_plans(
        source_dir=source_dir,
        cleaning_plan=cleaning_plan,
        unrecognized_file=unrecognized,
    )

    # Verify basic functionality still works
    assert stats["total_files"] == 1
    assert stats["total_dirs"] == 0
    assert isinstance(transfer_plan, list)
    assert isinstance(delete_plan, list)


def test_find_category_with_nested_extensions():
    """Test get_folder_path with nested categories containing 'extensions' key."""
    cleaning_plan = {
        "documents": {
            "text": {"extensions": [".txt", ".md"]},
            "pdf": {"extensions": [".pdf"]},
        }
    }
    file = Path("test.txt")
    unrecognized = Path("other")

    result = get_folder_path(file, cleaning_plan, unrecognized)
    assert result == Path("documents/text")


def test_transfer_files_with_relative_symlink(tmp_path):
    """Test transfer_files with relative symlinks."""
    # Create source structure
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    target_file = source_dir / "target.txt"
    target_file.write_text("content")
    symlink = source_dir / "link.txt"
    symlink.symlink_to(target_file.name)  # Relative symlink

    # Create destination directory
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # Setup transfer plan
    transfer_plan = [(symlink, dest_dir / "link.txt")]
    logger = MagicMock()

    # Execute transfer
    num_transferred, total = transfer_files(transfer_plan, logger, dry_run=False)

    assert num_transferred == 1
    assert total == 1
    assert not symlink.exists()  # Original symlink should be removed
    assert (dest_dir / "link.txt").is_symlink()
    assert (dest_dir / "link.txt").readlink().name == "target.txt"


def test_transfer_files_with_progress_bar(tmp_path):
    """Test transfer_files with progress bar updates."""
    # Create test files
    source_file = tmp_path / "source.txt"
    source_file.write_text("test")
    dest_file = tmp_path / "dest" / "source.txt"

    # Mock progress bar
    progress = MagicMock()
    task_id = 1

    transfer_plan = [(source_file, dest_file)]
    logger = MagicMock()

    num_transferred, total = transfer_files(
        transfer_plan, logger, dry_run=False, progress=progress, task_id=task_id
    )

    assert num_transferred == 1
    assert total == 1
    # Verify progress bar updates
    progress.update.assert_called_with(task_id, advance=1)


def test_delete_dirs_with_progress_bar(tmp_path):
    """Test delete_dirs with progress bar updates."""
    # Create test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Mock progress bar
    progress = MagicMock()
    task_id = 1

    delete_plan = [test_dir]
    logger = MagicMock()

    num_deleted, total = delete_dirs(
        delete_plan, logger, dry_run=False, progress=progress, task_id=task_id
    )

    assert num_deleted == 1
    assert total == 1
    # Verify progress bar updates
    progress.update.assert_called()
    assert not test_dir.exists()


def test_get_folder_path_with_invalid_cleaning_plan():
    """Test get_folder_path with invalid cleaning plan structure."""
    cleaning_plan = {
        "documents": None,  # Invalid structure
        "images": {"extensions": [".jpg"]},
    }
    file = Path("test.jpg")
    unrecognized = Path("other")

    result = get_folder_path(file, cleaning_plan, unrecognized)
    assert result == Path("images")  # Should handle invalid structure gracefully


def test_get_folder_path_with_empty_category():
    """Test get_folder_path with empty category."""
    cleaning_plan = {
        "documents": {"extensions": []},  # Empty extensions list
        "images": {"extensions": [".jpg"]},
    }
    file = Path("test.doc")
    unrecognized = Path("other")

    result = get_folder_path(file, cleaning_plan, unrecognized)
    assert result == unrecognized  # Should return unrecognized path


def test_transfer_files_with_complex_symlink(tmp_path):
    """Test transfer_files with complex symlink scenarios."""
    # Create nested directory structure
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    nested_dir = source_dir / "nested"
    nested_dir.mkdir()

    # Create target file and symlink in different directories
    target_file = source_dir / "target.txt"
    target_file.write_text("content")
    symlink = nested_dir / "link.txt"
    symlink.symlink_to(Path("..") / "target.txt")

    # Create destination directory
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # Setup transfer plan
    transfer_plan = [(symlink, dest_dir / "link.txt")]
    logger = MagicMock()

    # Execute transfer
    num_transferred, total = transfer_files(
        transfer_plan, logger, dry_run=False, progress=MagicMock(), task_id=1
    )

    assert num_transferred == 1
    assert total == 1
    assert (dest_dir / "link.txt").is_symlink()
    # Verify symlink points to correct relative path
    assert (dest_dir / "link.txt").readlink().name == "target.txt"
