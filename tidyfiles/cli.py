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
        help="Number of sessions to show",
    ),
    session_id: int = typer.Option(
        None,
        "--session",
        "-s",
        help="Show details for a specific session",
    ),
):
    """Show the history of file organization operations.

    The history is organized into sessions, where each session represents one run of
    the tidyfiles command. By default, shows a list of all sessions with their source
    and destination directories.

    Examples:
        View all sessions (latest first):
            $ tidyfiles history

        View only the last 5 sessions:
            $ tidyfiles history --limit 5

        View details of a specific session:
            $ tidyfiles history --session 3
    """
    if history_file is None:
        history_file = get_default_history_file()
    else:
        history_file = Path(history_file)

    history = OperationHistory(history_file)
    sessions = history.sessions[-limit:] if limit > 0 else history.sessions

    if not sessions:
        console.print("[yellow]No sessions in history[/yellow]")
        return

    if session_id is not None:
        # Show detailed view of a specific session
        session = next((s for s in history.sessions if s["id"] == session_id), None)
        if not session:
            console.print(f"[red]Session {session_id} not found[/red]")
            return

        operations = session.get("operations", [])
        session_start = datetime.fromisoformat(session["start_time"])

        # Ensure operations is a list
        if not isinstance(operations, list):
            operations = []

        session_info = (
            f"\n[bold]Session Details[/bold]\n"
            f"Started: [magenta]{session_start.strftime('%Y-%m-%d %H:%M:%S')}[/magenta]\n"
            f"Source: [blue]{session['source_dir'] if session['source_dir'] else 'N/A'}[/blue]\n"
            f"Destination: [blue]{session['destination_dir'] if session['destination_dir'] else 'N/A'}[/blue]\n"
            f"Status: [yellow]{session['status']}[/yellow]\n"
            f"Operations: [cyan]{len(operations)}[/cyan]"
        )
        console.print(session_info)

        # Show operations list or no operations message
        if not operations:
            console.print(f"[yellow]No operations in session {session_id}[/yellow]")
            return

        # Show detailed operation table for the session
        table = Table(title=f"Session {session_id} Operations")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Time", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Source", style="blue")
        table.add_column("Destination", style="blue")
        table.add_column("Status", style="yellow")

        for i, op in enumerate(operations, 1):
            timestamp = datetime.fromisoformat(op["timestamp"])
            table.add_row(
                str(i),
                timestamp.strftime("%H:%M:%S"),
                op["type"],
                op["source"],
                op["destination"],
                op["status"],
            )

        console.print(table)

    else:
        # Show sessions overview
        table = Table(title="Operation Sessions")
        table.add_column("Session ID", justify="right", style="cyan")
        table.add_column("Date", style="magenta")
        table.add_column("Time", style="magenta")
        table.add_column("Source", style="blue")
        table.add_column("Destination", style="blue")
        table.add_column("Operations", justify="right", style="cyan")
        table.add_column("Status", style="yellow")

        for session in reversed(sessions):
            start_time = datetime.fromisoformat(session["start_time"])
            # Format paths to be more readable
            source = session.get("source_dir", "N/A")
            if source and len(source) > 30:
                source = "..." + source[-27:]

            dest = session.get("destination_dir", "N/A")
            if dest and len(dest) > 30:
                dest = "..." + dest[-27:]

            table.add_row(
                str(session["id"]),
                start_time.strftime("%Y-%m-%d"),
                start_time.strftime("%H:%M:%S"),
                "N/A"
                if session.get("source_dir") in [None, "None"]
                else str(session["source_dir"]),
                "N/A"
                if session.get("destination_dir") in [None, "None"]
                else str(session["destination_dir"]),
                str(len(session["operations"])),
                session["status"],
            )

        console.print(table)
        console.print(
            "\n[dim]Use --session/-s <ID> to view details of a specific session[/dim]"
        )


@app.command()
def undo(
    session_id: int = typer.Option(
        None,
        "--session",
        "-s",
        help="Session ID to undo operations from",
    ),
    operation_number: int = typer.Option(
        None,
        "--number",
        "-n",
        help="Operation number within the session to undo",
    ),
    history_file: str = typer.Option(
        None,
        "--history-file",
        help="Path to the history file",
        show_default=False,
    ),
):
    """Undo file organization operations.

    Operations can be undone at two levels:
    1. Session level - undo all operations in a session
    2. Operation level - undo a specific operation within a session

    When undoing operations, files will be moved back to their original locations
    and deleted directories will be restored. Each operation is handled independently,
    so you can safely undo specific operations without affecting others.

    Examples:
        Undo all operations in the latest session:
            $ tidyfiles undo

        Undo all operations in a specific session:
            $ tidyfiles undo --session 3

        Undo a specific operation in a session:
            $ tidyfiles undo --session 3 --number 2

    Use 'tidyfiles history' to see available sessions and operations.
    """
    if history_file is None:
        history_file = get_default_history_file()
    else:
        history_file = Path(history_file)

    history = OperationHistory(history_file)

    if not history.sessions:
        console.print("[yellow]No sessions in history[/yellow]")
        return

    # If no session specified, use the latest session
    if session_id is None:
        session = history.sessions[-1]
        session_id = session["id"]
    else:
        session = next((s for s in history.sessions if s["id"] == session_id), None)
        if not session:
            console.print(f"[red]Session {session_id} not found[/red]")
            return

    operations = session["operations"]
    if not operations:
        console.print(f"[yellow]No operations in session {session_id}[/yellow]")
        return

    if operation_number is not None:
        # Undo specific operation in the session
        if operation_number < 1 or operation_number > len(operations):
            console.print(f"[red]Invalid operation number: {operation_number}[/red]")
            return

        operation = operations[operation_number - 1]
    else:
        # Show session summary and confirm undoing all operations
        session_start = datetime.fromisoformat(session["start_time"])
        console.print(
            Panel(
                f"Session to undo:\n"
                f"Session ID: [cyan]{session['id']}[/cyan]\n"
                f"Started: [magenta]{session_start.strftime('%Y-%m-%d %H:%M:%S')}[/magenta]\n"
                f"Operations: [blue]{len(operations)}[/blue]\n"
                f"Status: [yellow]{session['status']}[/yellow]",
                title="[bold cyan]Undo Session[/bold cyan]",
                expand=False,
            )
        )

        if typer.confirm("Do you want to undo all operations in this session?"):
            # Undo all operations in reverse order
            success = True
            for i in reversed(range(len(operations))):
                if not history.undo_operation(session_id, i):
                    console.print("[red]Failed to undo all operations[/red]")
                    success = False
                    break
            if success:
                console.print(
                    "[green]All operations in session successfully undone![/green]"
                )
            return
        else:
            console.print("[yellow]Operation cancelled[/yellow]")
            return

    # Show operation details and confirm
    console.print(
        Panel(
            f"Operation to undo:\n"
            f"Type: [cyan]{operation['type']}[/cyan]\n"
            f"Source: [blue]{operation['source']}[/blue]\n"
            f"Destination: [blue]{operation['destination']}[/blue]\n"
            f"Status: [yellow]{operation['status']}[/yellow]",
            title="[bold cyan]Undo Operation[/bold cyan]",
            expand=False,
        )
    )

    if typer.confirm("Do you want to undo this operation?"):
        # Undo just this specific operation
        if history.undo_operation(session_id, operation_number - 1):
            console.print("[green]Operation successfully undone![/green]")
        else:
            console.print("[red]Failed to undo operation[/red]")
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
            # Start a new session for this organization run
            history.start_session(
                source_dir=settings["source_dir"],
                destination_dir=settings["destination_dir"],
            )

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
