import shutil
from pathlib import Path

import loguru


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
    for source, destination in transfer_plan:
        copy_number = 1
        while destination.exists():
            destination = destination.with_name(
                f"{destination.stem}_{copy_number}{destination.suffix}"
            )
            copy_number += 1
        if dry_run:
            logger.info(f"[DRY-RUN] Would transfer {source} to {destination}")
        else:
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                source.replace(destination)
                logger.info(f"Transferred {source} to {destination}")
                num_transferred_files += 1
            except Exception as e:
                logger.error(f"Error transferring {source} to {destination}: {e}")
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
    num_deleted_directories = 0
    for directory in delete_plan:
        if dry_run:
            logger.info(f"[DRY-RUN] Would delete {directory}")
        else:
            try:
                shutil.rmtree(directory)
                logger.info(f"Deleted {directory}")
                num_deleted_directories += 1
            except Exception as e:
                logger.error(f"Error deleting {directory}: {e}")
    return num_deleted_directories, len(delete_plan)
