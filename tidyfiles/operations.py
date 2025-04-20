import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Protocol

from rich.console import Console
from rich.panel import Panel
import loguru

from .history import OperationHistory
from .security import SystemSecurity


class ProgressBarProtocol(Protocol):
    """Protocol for progress bar objects to avoid importing Rich's Progress directly.

    This defines the minimum interface required for progress bar objects used in this module.
    Using a Protocol instead of Any improves type checking while maintaining flexibility.
    """

    def update(
        self, task_id: int, advance: Optional[float] = None, **kwargs
    ) -> None: ...
    def add_task(
        self, description: str, total: Optional[float] = None, **kwargs
    ) -> int: ...


console = Console()


def get_folder_path(
    file: Path, cleaning_plan: Dict[str, Any], unrecognized_file: Path
) -> Path:
    """Determine the folder for a given file based on its extension.

    Supports nested categories in the cleaning plan.

    Args:
        file (Path): The file to determine the folder for.
        cleaning_plan (Dict[str, Any]): The cleaning plan with possible nested categories.
        unrecognized_file (Path): The folder to return when the file extension is not found.

    Returns:
        Path: The folder for the given file.
    """

    def find_category(
        plan: Dict[str, Any], extension: str, current_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Recursively find the category for a file extension in a nested cleaning plan.

        This helper function traverses the cleaning plan dictionary to find the appropriate
        category for a given file extension. It supports nested categories and returns the
        full path to the category folder.

        Args:
            plan (Dict[str, Any]): The cleaning plan dictionary or sub-dictionary to search in.
            extension (str): The file extension to find (including the dot, e.g., '.txt').
            current_path (Optional[Path]): The current path being built during recursion.

        Returns:
            Optional[Path]: The relative path to the category folder if found, None otherwise.
        """
        for category, value in plan.items():
            if isinstance(value, dict):
                # If this is a nested category with "extensions" key, check it first
                if "extensions" in value and extension in value["extensions"]:
                    return current_path / category if current_path else Path(category)

                # Recursively search in subcategories
                sub_path = find_category(
                    value,
                    extension,
                    current_path / category if current_path else Path(category),
                )
                if sub_path:
                    return sub_path
            elif isinstance(value, list) and extension in value:
                return current_path / category if current_path else Path(category)
        return None

    # Start search from the root of the cleaning plan
    result = find_category(cleaning_plan, file.suffix)
    return result if result else unrecognized_file


def create_plans(
    source_dir: Path,
    cleaning_plan: Dict[str, Any],
    unrecognized_file: Path,
    logger: Optional[loguru.logger] = None,
    strict_validation: bool = True,
    **kwargs,
) -> Tuple[List[Tuple[Path, Path]], List[Path], Dict[str, int]]:
    """Generate plans for file transfers and directory deletions.

    Scans the source directory, creating a plan to move files based on the
    cleaning plan and a plan to delete directories found during the scan.
    Supports nested categories in the cleaning plan and excluding specific paths.

    Args:
        source_dir (Path): The directory to scan.
        cleaning_plan (Dict[str, Any]): Configuration mapping file extensions to destination folders.
        unrecognized_file (Path): The base path for files with unrecognized extensions.
        logger (Optional[loguru.logger]): Logger instance for logging operations.
        strict_validation (bool): If True (default), prevents operations in system directories
        **kwargs: Optional arguments. Supports 'excludes' (Set[Path]): Paths to ignore.

    Returns:
        Tuple[List[Tuple[Path, Path]], List[Path], Dict[str, int]]: A tuple containing:
            - transfer plan (list of source/destination pairs)
            - delete plan (list of directories)
            - statistics dictionary with total counts
    """
    # Validate source directory
    SystemSecurity.validate_path(source_dir, strict=strict_validation)

    # Validate all target directories in cleaning plan
    for target_dir in cleaning_plan.keys():
        SystemSecurity.validate_path(Path(target_dir), strict=strict_validation)

    # Validate unrecognized file directory
    SystemSecurity.validate_path(unrecognized_file, strict=strict_validation)

    transfer_plan = []
    delete_plan = []
    excludes = kwargs.get("excludes", set()) or set()

    # Get all target directories from cleaning plan
    target_dirs = {Path(dir) for dir in cleaning_plan.keys()}
    target_dirs.add(unrecognized_file)

    # Track total counts
    total_files = 0
    total_dirs = 0

    for filesystem_object in source_dir.rglob("*"):
        # Skip if the object is in excludes
        if any(filesystem_object.is_relative_to(excluded) for excluded in excludes):
            continue

        if filesystem_object.is_dir():
            total_dirs += 1
            # Only add to delete plan if not in target directories
            if not any(
                filesystem_object.is_relative_to(target) for target in target_dirs
            ):
                delete_plan.append(filesystem_object)
        elif filesystem_object.is_file():
            total_files += 1
            destination_folder = get_folder_path(
                filesystem_object, cleaning_plan, unrecognized_file
            )
            destination = destination_folder / filesystem_object.name

            # Only add to transfer plan if the file will actually move
            if destination.parent != filesystem_object.parent:
                transfer_plan.append((filesystem_object, destination))

    # Log the overall statistics if logger is provided
    if logger:
        logger.info(
            f"Found {total_files} total files ({len(transfer_plan)} to transfer) and "
            f"{total_dirs} total directories ({len(delete_plan)} to delete)"
        )

    stats = {
        "total_files": total_files,
        "total_dirs": total_dirs,
        "files_to_transfer": len(transfer_plan),
        "dirs_to_delete": len(delete_plan),
    }

    return transfer_plan, delete_plan, stats


def transfer_files(
    transfer_plan: List[Tuple[Path, Path]],
    logger: loguru.logger,
    dry_run: bool,
    history: Optional[OperationHistory] = None,
    progress: Optional[ProgressBarProtocol] = None,
    task_id: Optional[int] = None,
    strict_validation: bool = True,
) -> Tuple[int, int]:
    """
    Move files to designated folders based on sorting plan.

    If the destination file already exists, the function will create a new file
    with a copy number appended to the filename (e.g. "example.txt" would become
    "example_1.txt").

    Args:
        transfer_plan (List[Tuple[Path, Path]]): A list of tuples, where the first
            element is the source file and the second element is the destination
            folder.
        logger: The logger to use for logging.
        dry_run (bool): Whether to perform a dry run (i.e. do not actually move
            the files).
        history (Optional[OperationHistory]): History tracker for operations.
        progress (Optional[ProgressBarProtocol]): Progress bar instance for displaying progress.
        task_id (Optional[int]): Task ID for the progress bar.
        strict_validation (bool): If True (default), prevents operations in system directories

    Returns:
        Tuple[int, int]: A tuple containing the number of files transferred and
            the total number of files in the transfer plan.
    """
    # Validate all paths in transfer plan
    for source, destination in transfer_plan:
        SystemSecurity.validate_path(source, strict=strict_validation)
        SystemSecurity.validate_path(destination.parent, strict=strict_validation)

    num_transferred_files = 0
    operations = []

    for i, (source, destination) in enumerate(transfer_plan):
        copy_number = 1
        while destination.exists():
            destination = destination.with_name(
                f"{destination.stem}_{copy_number}{destination.suffix}"
            )
            copy_number += 1

        if progress and task_id is not None:
            progress.update(task_id, advance=0, description=f"Moving: {source.name}")

        if history and not dry_run:
            history.add_operation("move", source, destination, datetime.now())

        if dry_run:
            msg = f"MOVE_FILE [DRY-RUN] | FROM: {source} | TO: {destination}"
            operations.append(f"[yellow]{msg}[/yellow]")
            logger.info(msg)
        else:
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if source.is_symlink():
                    # Get the target before moving
                    target = source.readlink()
                    # If it's a relative path, adjust it relative to the new location
                    if not target.is_absolute():
                        target = Path(
                            os.path.relpath(source.parent / target, destination.parent)
                        )
                    # Remove existing symlink if any
                    destination.unlink(missing_ok=True)
                    # Create new symlink
                    destination.symlink_to(target)
                    source.unlink()
                else:
                    source.replace(destination)

                msg = f"MOVE_FILE [SUCCESS] | FROM: {source} | TO: {destination}"
                operations.append(f"[green]{msg}[/green]")
                logger.info(msg)
                num_transferred_files += 1
            except Exception as e:
                error_msg = (
                    f"MOVE_FILE [FAILED] | FROM: {source} | "
                    f"TO: {destination} | ERROR: {str(e)}"
                )
                operations.append(f"[red]{error_msg}[/red]")
                logger.error(error_msg)

        if progress and task_id is not None:
            progress.update(task_id, advance=1)

    # Only show summary if actual changes were made
    if operations and not progress:
        summary = (
            f"Total files processed: {len(transfer_plan)}\n"
            f"Successfully moved: [green]{num_transferred_files}[/green]\n"
            f"Failed: [red]{len(transfer_plan) - num_transferred_files}[/red]"
        )

        panel_content = "\n".join(
            [
                "[bold cyan]=== File Transfer Operations ===[/bold cyan]",
                *operations,
                "\n[bold cyan]=== File Transfer Summary ===[/bold cyan]",
                summary,
            ]
        )
        console.print(Panel(panel_content))
        logger.info(
            "=== File Transfer Summary ===\n"
            f"Total files processed: {len(transfer_plan)}\n"
            f"Successfully moved: {num_transferred_files}\n"
            f"Failed: {len(transfer_plan) - num_transferred_files}"
        )

    return num_transferred_files, len(transfer_plan)


def delete_dirs(
    delete_plan: List[Path],
    logger: loguru.logger,
    dry_run: bool,
    history: Optional[OperationHistory] = None,
    progress: Optional[ProgressBarProtocol] = None,
    task_id: Optional[int] = None,
    strict_validation: bool = True,
) -> Tuple[int, int]:
    """
    Delete empty directories after moving files.
    Only logs actual deletions while maintaining full history for undo operations.

    Args:
        delete_plan (List[Path]): A list of directories to delete.
        logger: The logger to use for logging.
        dry_run (bool): Whether to perform a dry run (i.e. do not actually delete
            the directories).
        history (Optional[OperationHistory]): History tracker for operations.
        progress (Optional[ProgressBarProtocol]): Progress bar instance for displaying progress.
        task_id (Optional[int]): Task ID for the progress bar.
        strict_validation (bool): If True (default), prevents operations in system directories

    Returns:
        Tuple[int, int]: A tuple containing the number of directories deleted and
            the total number of directories in the delete plan.
    """
    # Validate all paths in delete plan
    for directory in delete_plan:
        SystemSecurity.validate_path(directory, strict=strict_validation)

    num_deleted_directories = 0
    operations = []

    # Sort directories by depth (deepest first) to handle nested directories properly
    sorted_delete_plan = sorted(delete_plan, key=lambda x: len(x.parts), reverse=True)

    for directory in sorted_delete_plan:
        if progress and task_id is not None:
            progress.update(
                task_id, advance=0, description=f"Cleaning: {directory.name}"
            )

        # Only log actual filesystem changes
        if dry_run:
            if directory.exists() and not any(directory.iterdir()):
                msg = f"DELETE_DIR [DRY-RUN] | PATH: {directory}"
                operations.append(f"[yellow]{msg}[/yellow]")
                logger.info(msg)
        else:
            try:
                if directory.exists() and not any(directory.iterdir()):
                    # Try to delete the directory first
                    directory.rmdir()

                    # Only record in history after successful deletion
                    if history:
                        try:
                            history.add_operation(
                                "delete", directory, directory, datetime.now()
                            )
                        except Exception as e:
                            # If history recording fails, try to restore the directory
                            try:
                                directory.mkdir()
                            except Exception:
                                pass  # If restoration fails, we can't do much about it
                            error_msg = f"DELETE_DIR [FAILED] | PATH: {directory} | ERROR: {str(e)}"
                            operations.append(f"[red]{error_msg}[/red]")
                            logger.error(error_msg)
                            continue

                    msg = f"DELETE_DIR [SUCCESS] | PATH: {directory}"
                    operations.append(f"[green]{msg}[/green]")
                    logger.info(msg)
                    num_deleted_directories += 1

            except Exception as e:
                error_msg = f"DELETE_DIR [FAILED] | PATH: {directory} | ERROR: {str(e)}"
                operations.append(f"[red]{error_msg}[/red]")
                logger.error(error_msg)

        if progress and task_id is not None:
            progress.update(task_id, advance=1)

    # Only show summary if actual changes were made
    if operations and not progress:
        summary = f"Successfully deleted: [green]{num_deleted_directories}[/green] directories"

        panel_content = "\n".join(
            [
                "[bold cyan]=== Directory Cleanup Operations ===[/bold cyan]",
                *operations,
                "\n[bold cyan]=== Directory Cleanup Summary ===[/bold cyan]",
                summary,
            ]
        )
        console.print(Panel(panel_content))
        logger.info(
            "=== Directory Cleanup Summary ===\n"
            f"Successfully deleted: {num_deleted_directories} directories"
        )

    return num_deleted_directories, len(delete_plan)
