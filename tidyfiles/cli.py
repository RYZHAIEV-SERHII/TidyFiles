import typer
from tidyfiles.config import get_settings
from tidyfiles.logger import get_logger
from tidyfiles.operations import create_plans, transfer_files, delete_dirs
from rich.console import Console
from rich.panel import Panel
from rich import box

app = typer.Typer()
console = Console()


def print_welcome_message(dry_run: bool, source_dir: str, destination_dir: str):
    mode_text = (
        "[bold yellow]DRY RUN MODE[/bold yellow] 🔍"
        if dry_run
        else "[bold green]LIVE MODE[/bold green] 🚀"
    )

    welcome_text = f"""
[bold cyan]TidyFiles[/bold cyan] 📁 - Your smart file organizer!

Current Mode: {mode_text}
Source Directory: [blue]{source_dir}[/blue]
Destination Directory: [blue]{destination_dir}[/blue]

[dim]Use --help for more options[/dim]
    """
    console.print(
        Panel(
            welcome_text,
            title="[bold cyan]Welcome[/bold cyan]",
            subtitle="[dim]Press Ctrl+C to cancel at any time[/dim]",
            box=box.ROUNDED,
            expand=True,
            padding=(1, 2),
        )
    )


@app.command()
def main(dry_run: bool = True):
    # Get settings
    settings = get_settings(
        source_dir="test_folder",
        destination_dir="test_folder_sorted",
        log_folder_name="logs",
    )

    print_welcome_message(
        dry_run=dry_run,
        source_dir=str(settings["source_dir"]),
        destination_dir=str(settings["destination_dir"]),
    )

    logger = get_logger(**settings)

    # Create plans for file transfer and directory deletion
    transfer_plan, delete_plan = create_plans(**settings)

    # Process files and directories using the already formatted output in operations.py
    num_transferred_files, total_files = transfer_files(transfer_plan, logger, dry_run)
    num_deleted_dirs, total_directories = delete_dirs(delete_plan, logger, dry_run)

    if not dry_run:
        final_summary = (
            "\n[bold green]=== Final Operation Summary ===[/bold green]\n"
            f"Files transferred: [cyan]{num_transferred_files}/{total_files}[/cyan]\n"
            f"Directories deleted: [cyan]{num_deleted_dirs}/{total_directories}[/cyan]"
        )
        console.print(Panel(final_summary))


if __name__ == "__main__":
    app()
