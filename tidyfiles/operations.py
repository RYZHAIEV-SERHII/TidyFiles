import shutil
from pathlib import Path

import loguru
from rich.console import Console
from rich.panel import Panel

console = Console()


def get_folder_path(
    file: Path, cleaning_plan: dict[Path, list[str]], unrecognized_file: Path
) -> Path:
    """Determine the folder for a given file based on its extension.

    If the file extension is not found in the cleaning plan, return the unrecognized file folder.

    Args:
        file (Path): The file to determine the folder for.
        cleaning_plan (dict[Path, list[str]]): The cleaning plan.
        unrecognized_file (Path): The folder to return when the file extension is not found.

    Returns:
        Path: The folder for the given file.
    """
    for folder_path, extensions in cleaning_plan.items():
        if file.suffix in extensions:
            return folder_path
    return unrecognized_file


def create_plans(
    source_dir: Path,
    cleaning_plan: dict[Path, list[str]],
    unrecognized_file: Path,
    **kwargs,
) -> tuple[list[tuple[Path, Path]], list[Path]]:
    """Generate file transfer and deletion plans.

    The transfer plan is a list of tuples, where the first element is the source file
    and the second element is the destination folder. The deletion plan is a list of
    directories to delete.

    Args:
        source_dir (Path): The source directory to scan.
        cleaning_plan (dict[Path, list[str]]): The cleaning plan.
        unrecognized_file (Path): The folder to move files to that are not found in the cleaning plan.
        **kwargs: Additional keyword arguments. Used just for simplifying settings passing.

    Returns:
        tuple[list[tuple[Path, Path]], list[Path]]: The transfer plan and the deletion plan.
    """
    transfer_plan = []
    delete_plan = []

    for filesystem_object in source_dir.rglob("*"):
        if filesystem_object.is_dir():
            delete_plan.append(filesystem_object)
        elif filesystem_object.is_file():
            destination_folder = get_folder_path(
                filesystem_object, cleaning_plan, unrecognized_file
            )
            transfer_plan.append(
                (filesystem_object, destination_folder / filesystem_object.name)
            )

    return transfer_plan, delete_plan


def transfer_files(
    transfer_plan: list[tuple[Path, Path]], logger: loguru.logger, dry_run: bool
) -> tuple[int, int]:
    """
    Move files to designated folders based on sorting plan.

    If the destination file already exists, the function will create a new file
    with a copy number appended to the filename (e.g. "example.txt" would become
    "example_1.txt").

    Args:
        transfer_plan (list[tuple[Path, Path]]): A list of tuples, where the first
            element is the source file and the second element is the destination
            folder.
        logger (loguru.logger): The logger to use for logging.
        dry_run (bool): Whether to perform a dry run (i.e. do not actually move
            the files).

    Returns:
        tuple[int, int]: A tuple containing the number of files transferred and
            the total number of files in the transfer plan.
    """
    num_transferred_files = 0
    console.print(
        "\n[bold cyan]=== Starting File Transfer Operations ===[/bold cyan]\n"
    )

    for source, destination in transfer_plan:
        copy_number = 1
        while destination.exists():
            destination = destination.with_name(
                f"{destination.stem}_{copy_number}{destination.suffix}"
            )
            copy_number += 1

        if dry_run:
            console.print(
                f"[yellow]MOVE_FILE [DRY-RUN] | FROM: {source} | TO: {destination}[/yellow]"
            )
            logger.info(f"MOVE_FILE [DRY-RUN] | FROM: {source} | TO: {destination}")
        else:
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                source.replace(destination)
                console.print(
                    f"[green]MOVE_FILE [SUCCESS] | FROM: {source} | TO: {destination}[/green]"
                )
                logger.info(f"MOVE_FILE [SUCCESS] | FROM: {source} | TO: {destination}")
                num_transferred_files += 1
            except Exception as e:
                error_msg = (
                    "MOVE_FILE [FAILED] | "
                    f"FROM: {source} | "
                    f"TO: {destination} | "
                    f"ERROR: {str(e)}"
                )
                console.print(f"[red]{error_msg}[/red]")
                logger.error(error_msg)

    summary = (
        "\n[bold cyan]=== File Transfer Summary ===[/bold cyan]\n"
        f"Total files processed: {len(transfer_plan)}\n"
        f"Successfully moved: [green]{num_transferred_files}[/green]\n"
        f"Failed: [red]{len(transfer_plan) - num_transferred_files}[/red]"
    )
    console.print(Panel(summary))
    logger.info(
        "=== File Transfer Summary ===\n"
        f"Total files processed: {len(transfer_plan)}\n"
        f"Successfully moved: {num_transferred_files}\n"
        f"Failed: {len(transfer_plan) - num_transferred_files}"
    )
    return num_transferred_files, len(transfer_plan)


def delete_dirs(
    delete_plan: list[Path], logger: loguru.logger, dry_run: bool
) -> tuple[int, int]:
    """
    Delete empty directories after moving files.

    Args:
        delete_plan (list[Path]): A list of directories to delete.
        logger (loguru.logger): The logger to use for logging.
        dry_run (bool): Whether to perform a dry run (i.e. do not actually delete
            the directories).

    Returns:
        tuple[int, int]: A tuple containing the number of directories deleted and
            the total number of directories in the delete plan.
    """
    deleted_paths = set()
    num_deleted_directories = 0
    console.print(
        "\n[bold cyan]=== Starting Directory Cleanup Operations ===[/bold cyan]\n"
    )

    for directory in delete_plan:
        if any(directory.is_relative_to(deleted) for deleted in deleted_paths):
            skip_msg = (
                "DELETE_DIR [SKIPPED] | "
                f"PATH: {directory} | "
                "REASON: Already deleted with parent directory"
            )
            console.print(f"[yellow]{skip_msg}[/yellow]")
            logger.info(skip_msg)
            num_deleted_directories += 1
            continue

        if dry_run:
            console.print(f"[yellow]DELETE_DIR [DRY-RUN] | PATH: {directory}[/yellow]")
            logger.info(f"DELETE_DIR [DRY-RUN] | PATH: {directory}")
        else:
            try:
                if directory.exists():
                    shutil.rmtree(directory)
                    deleted_paths.add(directory)
                    console.print(
                        f"[green]DELETE_DIR [SUCCESS] | PATH: {directory}[/green]"
                    )
                    logger.info(f"DELETE_DIR [SUCCESS] | PATH: {directory}")
                    num_deleted_directories += 1
            except Exception as e:
                error_msg = f"DELETE_DIR [FAILED] | PATH: {directory} | ERROR: {str(e)}"
                console.print(f"[red]{error_msg}[/red]")
                logger.error(error_msg)

    summary = (
        "\n[bold cyan]=== Directory Cleanup Summary ===[/bold cyan]\n"
        f"Total directories processed: {len(delete_plan)}\n"
        f"Successfully deleted: [green]{num_deleted_directories}[/green]\n"
        f"Failed: [red]{len(delete_plan) - num_deleted_directories}[/red]"
    )
    console.print(Panel(summary))
    logger.info(
        "=== Directory Cleanup Summary ===\n"
        f"Total directories processed: {len(delete_plan)}\n"
        f"Successfully deleted: {num_deleted_directories}\n"
        f"Failed: {len(delete_plan) - num_deleted_directories}"
    )
    return num_deleted_directories, len(delete_plan)
