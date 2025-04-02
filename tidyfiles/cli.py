import typer
from pathlib import Path
from datetime import datetime
from rich.table import Table
from tidyfiles import __version__
from tidyfiles.config import get_settings, DEFAULT_SETTINGS
from tidyfiles.logger import get_logger
from tidyfiles.operations import create_plans, transfer_files, delete_dirs
from tidyfiles.history import OperationHistory
from rich.console import Console
from rich.panel import Panel
from rich import box

app = typer.Typer(
    name="tidyfiles",
    help="TidyFiles - Organize your files automatically by type.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


def version_callback(value: bool):
    if value:
        typer.echo(f"TidyFiles version: {__version__}")
        raise typer.Exit()


def get_default_history_file() -> Path:
    """Get the default history file path."""
    return (
        Path(DEFAULT_SETTINGS["history_folder_name"])
        / DEFAULT_SETTINGS["history_file_name"]
    )


@app.command()
def history(
    history_file: str = typer.Option(
        None,
        "--history-file",
        help="Path to the history file",
        show_default=False,
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Number of operations to show",
    ),
):
    """Show the history of file operations."""
    if history_file is None:
        history_file = get_default_history_file()
    else:
        history_file = Path(history_file)

    history = OperationHistory(history_file)
    operations = history.operations[-limit:] if limit > 0 else history.operations

    if not operations:
        console.print("[yellow]No operations in history[/yellow]")
        return

    table = Table(title="Operation History")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Date", style="magenta")
    table.add_column("Time", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Source", style="blue")
    table.add_column("Destination", style="blue")
    table.add_column("Status", style="yellow")

    for i, op in enumerate(reversed(operations), 1):
        timestamp = datetime.fromisoformat(op["timestamp"])
        table.add_row(
            str(i),
            timestamp.strftime("%Y-%m-%d"),
            timestamp.strftime("%H:%M:%S"),
            op["type"],
            op["source"],
            op["destination"],
            op["status"],
        )

    console.print(table)


@app.command()
def undo(
    operation_number: int = typer.Option(
        None,
        "--number",
        "-n",
        help="Operation number to undo (from history command)",
    ),
    history_file: str = typer.Option(
        None,
        "--history-file",
        help="Path to the history file",
        show_default=False,
    ),
):
    """Undo a file organization operation."""
    if history_file is None:
        history_file = get_default_history_file()
    else:
        history_file = Path(history_file)

    history = OperationHistory(history_file)

    if operation_number is not None:
        # Undo specific operation
        if operation_number < 1 or operation_number > len(history.operations):
            console.print(f"[red]Invalid operation number: {operation_number}[/red]")
            return

        # Get the operation to undo (operations are stored in chronological order)
        operation = history.operations[-operation_number]
    else:
        # Undo last operation
        operation = history.get_last_operation()
        if not operation:
            console.print("[yellow]No operations to undo[/yellow]")
            return

    console.print(
        Panel(
            f"Operation to undo:\n"
            f"Type: [cyan]{operation['type']}[/cyan]\n"
            f"Source: [blue]{operation['source']}[/blue]\n"
            f"Destination: [blue]{operation['destination']}[/blue]\n"
            f"Time: [dim]{operation['timestamp']}[/dim]",
            title="[bold cyan]Undo Operation[/bold cyan]",
            box=box.ROUNDED,
        )
    )

    if typer.confirm("Do you want to undo this operation?"):
        if operation_number is not None:
            # For specific operation, we need to undo all operations up to that point
            for _ in range(operation_number):
                if not history.undo_last_operation():
                    console.print("[red]Failed to undo operation[/red]")
                    return
        else:
            if not history.undo_last_operation():
                console.print("[red]Failed to undo operation[/red]")
                return
        console.print("[green]Operation successfully undone![/green]")
    else:
        console.print("[yellow]Operation cancelled[/yellow]")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    source_dir: str = typer.Option(
        None,
        "--source-dir",
        "-s",
        help="Source directory to organize",
        show_default=False,
    ),
    destination_dir: str = typer.Option(
        None,
        "--destination-dir",
        "-d",
        help="Destination directory for organized files",
        show_default=False,
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run/--no-dry-run", help="Run in dry-run mode (no actual changes)"
    ),
    unrecognized_file_name: str = typer.Option(
        DEFAULT_SETTINGS["unrecognized_file_name"],
        "--unrecognized-dir",
        help="Directory name for unrecognized files",
        show_default=False,
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
        show_default=False,
    ),
    log_file_level: str = typer.Option(
        DEFAULT_SETTINGS["log_file_level"],
        "--log-file-level",
        help="File logging level",
        show_default=False,
    ),
    log_file_name: str = typer.Option(
        DEFAULT_SETTINGS["log_file_name"],
        "--log-file-name",
        help="Name of the log file",
        show_default=False,
    ),
    log_folder_name: str = typer.Option(
        None, "--log-folder", help="Folder for log files", show_default=False
    ),
    settings_file_name: str = typer.Option(
        DEFAULT_SETTINGS["settings_file_name"],
        "--settings-file",
        help="Name of the settings file",
        show_default=False,
    ),
    settings_folder_name: str = typer.Option(
        DEFAULT_SETTINGS["settings_folder_name"],
        "--settings-folder",
        help="Folder for settings file",
        show_default=False,
    ),
    history_file: str = typer.Option(
        None,
        "--history-file",
        help="Path to the history file",
        show_default=False,
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
    # If no source_dir and no command is being executed, show help
    if not source_dir and not ctx.invoked_subcommand:
        # Force help display with all options
        ctx.get_help()
        raise typer.Exit(0)

    # If source_dir is provided, proceed with file organization
    if source_dir:
        # Validate source directory
        source_path = Path(source_dir)
        if not source_path.exists():
            console.print(f"[red]Source directory does not exist: {source_dir}[/red]")
            raise typer.Exit(1)

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

        # Initialize history system if not in dry-run mode
        history = None
        if not dry_run:
            history_file_path = (
                Path(history_file) if history_file else get_default_history_file()
            )
            history = OperationHistory(history_file_path)

        # Create plans for file transfer and directory deletion
        transfer_plan, delete_plan = create_plans(**settings)

        # Process files and directories
        num_transferred_files, total_files = transfer_files(
            transfer_plan, logger, dry_run, history
        )
        num_deleted_dirs, total_directories = delete_dirs(
            delete_plan, logger, dry_run, history
        )

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
