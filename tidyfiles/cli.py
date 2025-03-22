import typer
from tidyfiles import __version__
from tidyfiles.config import get_settings, DEFAULT_SETTINGS
from tidyfiles.logger import get_logger
from tidyfiles.operations import create_plans, transfer_files, delete_dirs
from rich.console import Console
from rich.panel import Panel
from rich import box

app = typer.Typer(help="TidyFiles - Organize your files automatically by type.")
console = Console()


def version_callback(value: bool):
    if value:
        typer.echo(f"TidyFiles version: {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    source_dir: str = typer.Option(
        None, "--source-dir", "-s", help="Source directory to organize"
    ),
    destination_dir: str = typer.Option(
        None,
        "--destination-dir",
        "-d",
        help="Destination directory for organized files",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run/--no-dry-run", help="Run in dry-run mode (no actual changes)"
    ),
    unrecognized_file_name: str = typer.Option(
        DEFAULT_SETTINGS["unrecognized_file_name"],
        "--unrecognized-dir",
        help="Directory name for unrecognized files",
    ),
    log_console_output: bool = typer.Option(
        DEFAULT_SETTINGS["log_console_output_status"],
        "--log-console/--no-log-console",
        help="Enable/disable console logging",
    ),
    log_file_output: bool = typer.Option(
        DEFAULT_SETTINGS["log_file_output_status"],
        "--log-file/--no-log-file",
        help="Enable/disable file logging",
    ),
    log_console_level: str = typer.Option(
        DEFAULT_SETTINGS["log_console_level"],
        "--log-console-level",
        help="Console logging level",
    ),
    log_file_level: str = typer.Option(
        DEFAULT_SETTINGS["log_file_level"],
        "--log-file-level",
        help="File logging level",
    ),
    log_file_name: str = typer.Option(
        DEFAULT_SETTINGS["log_file_name"],
        "--log-file-name",
        help="Name of the log file",
    ),
    log_folder_name: str = typer.Option(
        None, "--log-folder", help="Folder for log files"
    ),
    settings_file_name: str = typer.Option(
        DEFAULT_SETTINGS["settings_file_name"],
        "--settings-file",
        help="Name of the settings file",
    ),
    settings_folder_name: str = typer.Option(
        DEFAULT_SETTINGS["settings_folder_name"],
        "--settings-folder",
        help="Folder for settings file",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """TidyFiles - Organize your files automatically by type."""
    if not source_dir and not version:
        ctx.get_help()
        raise typer.Exit()

    if source_dir:
        # Get settings with CLI arguments
        settings = get_settings(
            source_dir=source_dir,
            destination_dir=destination_dir,
            unrecognized_file_name=unrecognized_file_name,
            log_console_output_status=log_console_output,
            log_file_output_status=log_file_output,
            log_console_level=log_console_level,
            log_file_level=log_file_level,
            log_file_name=log_file_name,
            log_folder_name=log_folder_name,
            settings_file_name=settings_file_name,
            settings_folder_name=settings_folder_name,
        )

        print_welcome_message(
            dry_run=dry_run,
            source_dir=str(settings["source_dir"]),
            destination_dir=str(settings["destination_dir"]),
        )

        logger = get_logger(**settings)

        # Create plans for file transfer and directory deletion
        transfer_plan, delete_plan = create_plans(**settings)

        # Process files and directories
        num_transferred_files, total_files = transfer_files(
            transfer_plan, logger, dry_run
        )
        num_deleted_dirs, total_directories = delete_dirs(delete_plan, logger, dry_run)

        if not dry_run:
            final_summary = (
                "\n[bold green]=== Final Operation Summary ===[/bold green]\n"
                f"Files transferred: [cyan]{num_transferred_files}/{total_files}[/cyan]\n"
                f"Directories deleted: [cyan]{num_deleted_dirs}/{total_directories}[/cyan]"
            )
            console.print(Panel(final_summary))


def print_welcome_message(dry_run: bool, source_dir: str, destination_dir: str):
    """
    Prints a welcome message to the console, indicating the current mode of operation
    (dry run or live), and displays the source and destination directories.

    Args:
        dry_run (bool): Flag indicating whether the application is running in dry-run mode.
        source_dir (str): The source directory path for organizing files.
        destination_dir (str): The destination directory path for organized files.
    """
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


if __name__ == "__main__":
    app()
