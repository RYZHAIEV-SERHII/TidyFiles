import typer
from tidyfiles.config import get_settings
from tidyfiles.logger import get_logger
from tidyfiles.operations import create_plans, transfer_files, delete_dirs
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main(dry_run: bool = False):
    # Get settings
    settings = get_settings(
        source_dir="test_folder",
        destination_dir="test_folder_sorted",
        log_folder_name="logs",
    )
    logger = get_logger(**settings)

    # Create plans for file transfer and directory deletion
    transfer_plan, delete_plan = create_plans(**settings)

    # Check if dry run mode is enabled
    if dry_run:
        console.print("[bold yellow]Dry Run Mode[/bold yellow]")
        for src, dst in transfer_plan:
            console.print(f"Would move {src} to {dst}")
        for directory in delete_plan:
            console.print(f"Would delete {directory}")
    # Perform file transfer and directory deletion operations if dry run mode is disabled
    else:
        num_transferred_files, total_files = transfer_files(
            transfer_plan, logger, dry_run
        )
        num_deleted_dirs, total_directories = delete_dirs(delete_plan, logger, dry_run)
        console.print(f"Transferred {num_transferred_files} files")
        console.print(f"Deleted {num_deleted_dirs} directories")


if __name__ == "__main__":
    app()
