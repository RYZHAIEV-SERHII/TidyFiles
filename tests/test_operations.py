from pathlib import Path
from tidyfiles.operations import create_plans, transfer_files, delete_dirs
import shutil
from tidyfiles.logger import get_logger


def test_create_plans_with_empty_dir(tmp_path):
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


def test_transfer_files_dry_run(sample_files, tmp_path, test_logger):
    settings = {
        "source_dir": sample_files,
        "destination_dir": tmp_path,
        "cleaning_plan": {
            tmp_path / "documents": [".pdf"],
            tmp_path / "images": [".jpg"],
        },
        "unrecognized_file": tmp_path / "other",
        "excludes": set(),
    }
    transfer_plan, _ = create_plans(**settings)
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=True)
    assert num_transferred == 0  # No actual transfers in dry run
    assert total > 0


def test_transfer_files_with_existing_files(sample_files, tmp_path, test_logger):
    # Create destination directory with existing file
    dest_dir = tmp_path / "documents"
    dest_dir.mkdir(parents=True)
    existing_file = dest_dir / "document.pdf"
    existing_file.touch()

    settings = {
        "source_dir": sample_files,
        "destination_dir": tmp_path,
        "cleaning_plan": {
            tmp_path / "documents": [".pdf"],
        },
        "unrecognized_file": tmp_path / "other",
        "excludes": set(),
    }

    transfer_plan, _ = create_plans(**settings)
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=False)

    # Check if file was renamed with _1 suffix
    assert (dest_dir / "document_1.pdf").exists()
    assert num_transferred > 0


def test_transfer_files_with_permission_error(
    sample_files, tmp_path, test_logger, monkeypatch
):
    """Test transfer_files with permission error"""

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    settings = {
        "source_dir": sample_files,
        "destination_dir": tmp_path,
        "cleaning_plan": {
            tmp_path / "documents": [".pdf"],
        },
        "unrecognized_file": tmp_path / "other",
        "excludes": set(),
    }

    transfer_plan, _ = create_plans(**settings)
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=False)
    assert num_transferred == 0
    assert total > 0


def test_delete_dirs_dry_run(sample_files, tmp_path, test_logger):
    nested_dir = sample_files / "nested"
    nested_dir.mkdir(exist_ok=True)

    delete_plan = [nested_dir]
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=True)

    assert num_deleted == 0
    assert total > 0
    assert nested_dir.exists()


def test_delete_dirs_with_permission_error(
    sample_files, tmp_path, test_logger, monkeypatch
):
    """Test delete_dirs with permission error"""

    def mock_rmdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "rmdir", mock_rmdir)

    delete_plan = [tmp_path / "test_dir"]
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)
    assert num_deleted == 0
    assert total > 0


def test_delete_dirs_with_non_empty_dir(
    sample_files, tmp_path, test_logger, monkeypatch
):
    def mock_rmtree(*args, **kwargs):
        raise OSError("Directory not empty")

    monkeypatch.setattr(shutil, "rmtree", mock_rmtree)  # Mock shutil.rmtree

    nested_dir = sample_files / "nested"
    nested_dir.mkdir(exist_ok=True)
    test_file = nested_dir / "test.txt"
    test_file.touch()

    delete_plan = [nested_dir]
    num_deleted, total = delete_dirs(delete_plan, test_logger, dry_run=False)

    assert num_deleted == 0
    assert total == 1
    assert nested_dir.exists()
    assert test_file.exists()


def test_transfer_files_with_mkdir_error(
    sample_files, tmp_path, test_logger, monkeypatch
):
    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    settings = {
        "source_dir": sample_files,
        "destination_dir": tmp_path,
        "cleaning_plan": {
            tmp_path / "documents": [".pdf"],
        },
        "unrecognized_file": tmp_path / "other",
        "excludes": set(),
    }

    transfer_plan, _ = create_plans(**settings)
    num_transferred, total = transfer_files(transfer_plan, test_logger, dry_run=False)

    assert num_transferred == 0


def test_transfer_files_with_errors(tmp_path, capsys):  # Changed to capsys
    source_file = tmp_path / "test.txt"
    source_file.write_text("test")

    transfer_plan = [(source_file, Path("/nonexistent/path/test.txt"))]

    logger = get_logger(
        log_file_path=tmp_path / "test.log",
        log_console_output_status=True,
        log_file_output_status=True,
        log_console_level="ERROR",
        log_file_level="ERROR",
        log_file_mode="w",
    )

    num_transferred, total = transfer_files(transfer_plan, logger, dry_run=False)
    assert num_transferred == 0
    assert total == 1

    # Check stderr output instead of caplog
    captured = capsys.readouterr()
    assert "Permission denied" in captured.err


def test_delete_dirs_with_errors(tmp_path, capsys):
    delete_plan = [Path("/nonexistent/path")]

    logger = get_logger(
        log_file_path=tmp_path / "test.log",
        log_console_output_status=True,
        log_file_output_status=True,
        log_console_level="ERROR",
        log_file_level="ERROR",
        log_file_mode="w",
    )

    num_deleted, total = delete_dirs(delete_plan, logger, dry_run=False)
    assert num_deleted == 0
    assert total == 1

    # Check both stdout and stderr
    captured = capsys.readouterr()
    combined_output = captured.out + captured.err
    assert any(
        msg in combined_output for msg in ["Failed: 1", "No such file or directory"]
    )
