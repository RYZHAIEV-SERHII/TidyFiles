import typer
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable
from rich.table import Table
from tidyfiles import __version__
from tidyfiles.config import get_settings, DEFAULT_SETTINGS
from tidyfiles.logger import get_logger
from tidyfiles.operations import (
    create_plans,
    transfer_files,
    delete_dirs,
    ProgressBarProtocol,
)
from tidyfiles.history import OperationHistory
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from loguru import logger as loguru_logger

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


def suppress_logs(func: Callable) -> Callable:
    """Decorator to suppress logs during function execution.

    This decorator temporarily disables all logging output while the wrapped function
    executes, then restores the default logging configuration afterward. This is useful
    for operations that would otherwise produce excessive log output that would clutter
    the display, such as when using progress bars.

    The decorator uses only the public API of the loguru logger to avoid accessing
    protected attributes, making it more robust against future changes in the library.

    Args:
        func: The function to wrap with log suppression

    Returns:
        Wrapped function that suppresses logs during execution

    Example:
        @suppress_logs
        def noisy_function():
            # This function's logs will be suppressed
            logger.info("This won't be displayed")
    """

    def wrapper(*args, **kwargs):
        # Create a temporary handler to get a handler ID without accessing protected attributes
        # This is a clean way to interact with loguru's handler system
        temp_id = loguru_logger.add(lambda _: None)
        loguru_logger.remove(temp_id)

        # Remove all existing handlers to suppress all logs
        # Using the public configure() API instead of accessing _core directly
        loguru_logger.configure(handlers=[])

        # Add a null handler that discards all logs below ERROR level
        # This ensures critical errors are still captured while suppressing info/debug logs
        null_handler_id = loguru_logger.add(lambda _: None, level="ERROR")

        try:
            # Execute the wrapped function with log suppression active
            return func(*args, **kwargs)
        finally:
            # Cleanup phase - restore normal logging
            # First remove our temporary null handler
            loguru_logger.remove(null_handler_id)

            # Then restore the default configuration with stderr output
            # This ensures logs will work normally after this function completes
            loguru_logger.configure(handlers=[])
            loguru_logger.add(sys.stderr)

    return wrapper


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


@app.command(
    help="Show operation history (use 'tidyfiles history --help' for details)."
)
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


@app.command(
    help="Undo operations from history (use 'tidyfiles undo --help' for details)."
)
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
            # Define Progress Bar Columns (Nala-style)
            progress_columns = [
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                TimeElapsedColumn(),
            ]

            # Use suppress_logs decorator to handle log suppression
            @suppress_logs
            def run_undo_operations():
                with Progress(
                    *progress_columns, console=console, transient=True
                ) as progress:
                    # Add task for undoing operations
                    undo_task_id = progress.add_task(
                        "Undoing operations...", total=len(operations)
                    )

                    # Undo all operations in reverse order
                    nonlocal success
                    success = True
                    for i in reversed(range(len(operations))):
                        # Cast progress to ProgressBarProtocol to satisfy type checker
                        progress_bar: ProgressBarProtocol = progress  # type: ignore
                        if not history.undo_operation(
                            session_id, i, progress_bar, undo_task_id
                        ):
                            console.print("[red]Failed to undo all operations[/red]")
                            success = False
                            break

            # Execute the function with log suppression
            success = True
            run_undo_operations()

            if success:
                console.print(
                    "[green]All operations in session successfully undone![/green]"
                )
            return
        else:
            console.print("[yellow]Operation cancelled[/yellow]")
            return

    # Show operation details and confirm
    try:
        op_details = (
            f"Operation to undo:\n"
            f"Type: [cyan]{operation.get('type', 'N/A')}[/cyan]\n"
            f"Source: [blue]{operation.get('source', 'N/A')}[/blue]\n"
            f"Destination: [blue]{operation.get('destination', 'N/A')}[/blue]\n"
            f"Status: [yellow]{operation.get('status', 'N/A')}[/yellow]"
        )
        console.print(
            Panel(
                op_details,
                title="[bold cyan]Undo Operation[/bold cyan]",
                expand=False,
            )
        )

        if typer.confirm("Do you want to undo this operation?"):
            # Define Progress Bar Columns (Nala-style)
            progress_columns = [
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                TimeElapsedColumn(),
            ]

            # Use suppress_logs decorator to handle log suppression
            @suppress_logs
            def run_undo_operation():
                with Progress(
                    *progress_columns, console=console, transient=True
                ) as progress:
                    # Add task for undoing operation
                    undo_task_id = progress.add_task("Undoing operation...", total=1)

                    # Undo just this specific operation
                    # Cast progress to ProgressBarProtocol to satisfy type checker
                    progress_bar: ProgressBarProtocol = progress  # type: ignore
                    if history.undo_operation(
                        session_id, operation_number - 1, progress_bar, undo_task_id
                    ):
                        console.print("[green]Operation successfully undone![/green]")
                    else:
                        console.print("[red]Failed to undo operation[/red]")

            # Execute the function with log suppression
            run_undo_operation()
        else:
            console.print("[yellow]Operation cancelled[/yellow]")

    except Exception as e:
        # Catch unexpected errors accessing potentially corrupt data
        # or during the undo process itself for this specific operation.
        console.print(
            f"[red]Error processing undo for operation {operation_number}: {e}[/red]"
        )
        console.print(
            "[yellow]Operation may be corrupt or could not be undone.[/yellow]"
        )
        # Ensure graceful exit even if error occurs
        raise typer.Exit(0)


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
        # Record start time for duration calculation
        start_time = time.time()

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

        logger.info(
            f"Plan created: {len(transfer_plan)} files to transfer, {len(delete_plan)} directories potentially to delete."
        )
        console.print(f"Found {len(transfer_plan)} files to potentially transfer.")
        console.print(f"Found {len(delete_plan)} directories to potentially delete.")

        # Define Progress Bar Columns (Nala-style)
        progress_columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
        ]

        # Use suppress_logs decorator to handle log suppression
        @suppress_logs
        def run_file_operations():
            nonlocal \
                num_transferred_files, \
                total_files, \
                num_deleted_dirs, \
                total_directories

            with Progress(
                *progress_columns, console=console, transient=True
            ) as progress:
                if transfer_plan:
                    transfer_task_id = progress.add_task(
                        "Moving files...", total=len(transfer_plan)
                    )
                    # Cast progress to ProgressBarProtocol to satisfy type checker
                    progress_bar: ProgressBarProtocol = progress  # type: ignore
                    num_transferred_files, total_files = transfer_files(
                        transfer_plan,
                        logger,
                        dry_run,
                        history,
                        progress=progress_bar,
                        task_id=transfer_task_id,
                    )
                else:
                    console.print("[yellow]No files found to transfer.[/yellow]")
                    num_transferred_files, total_files = 0, 0

                if delete_plan:
                    delete_task_id = progress.add_task(
                        "Cleaning directories...", total=len(delete_plan)
                    )
                    # Cast progress to ProgressBarProtocol to satisfy type checker
                    progress_bar: ProgressBarProtocol = progress  # type: ignore
                    num_deleted_dirs, total_directories = delete_dirs(
                        delete_plan,
                        logger,
                        dry_run,
                        history,
                        progress=progress_bar,
                        task_id=delete_task_id,
                    )
                else:
                    console.print("[yellow]No directories found to clean.[/yellow]")
                    num_deleted_dirs, total_directories = 0, 0

        # Initialize variables before calling the function
        num_transferred_files, total_files = 0, 0
        num_deleted_dirs, total_directories = 0, 0

        # Execute the function with log suppression
        run_file_operations()

        # Record end time and calculate duration
        end_time = time.time()
        duration = end_time - start_time
        duration_str = str(timedelta(seconds=int(duration)))

        # Create a Nala-style summary display
        if total_files > 0 or total_directories > 0:
            # Calculate percentages
            file_percent = (
                100.0
                if total_files == 0
                else (num_transferred_files / total_files) * 100
            )
            dir_percent = (
                100.0
                if total_directories == 0
                else (num_deleted_dirs / total_directories) * 100
            )

            # Create summary panel
            summary_lines = []

            # Add separator at the top for spacing
            summary_lines.append("")

            # Add progress bars directly in the summary with more details
            if total_files > 0:
                # Create a more verbose and aligned file progress bar
                file_label = "[green]✓[/green] [blue]Files Progress:[/blue]      "
                file_bar = f"[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan] [blue]{file_percent:.1f}%[/blue] • {duration_str} • {num_transferred_files}/{total_files}"
                summary_lines.append(f"{file_label}{file_bar}")

            if total_directories > 0:
                # Create a more verbose and aligned directory progress bar
                dir_label = "[green]✓[/green] [blue]Directories Progress:[/blue]"
                dir_bar = f"[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan] [blue]{dir_percent:.1f}%[/blue] • {duration_str} • {num_deleted_dirs}/{total_directories}"
                summary_lines.append(f"{dir_label}{dir_bar}")

            # Add separator before status information
            summary_lines.append("")

            # Add time taken at the bottom
            summary_lines.append(f"Time Taken: [blue]{duration_str}[/blue]")

            # Add completion status at the bottom
            if dry_run:
                summary_lines.append(
                    "Status: [yellow]Dry Run (no changes made)[/yellow]"
                )
            else:
                summary_lines.append("Status: [green]Complete[/green]")

            # Create the summary panel with everything included
            summary_panel = Panel(
                "\n".join(summary_lines),
                title="[bold green]Operation Summary[/bold green]",
                border_style="green",
                padding=(1, 2),
                expand=False,
                box=box.ROUNDED,
            )

            console.print("\n")
            console.print(summary_panel)

            # No need for separate progress bars since they're now included in the summary
        else:
            # No operations performed
            console.print(
                Panel(
                    "No files or directories were processed.",
                    title="[bold yellow]Operation Summary[/bold yellow]",
                    border_style="yellow",
                    padding=(1, 2),
                    expand=False,
                    box=box.ROUNDED,
                )
            )

        # Update history if not in dry run mode
        if not dry_run and history:
            # Update current session status to completed if it exists
            if history.current_session is not None:
                history.current_session["status"] = "Completed"
                history._save_history()

            # Print completion message
            console.print("\n[bold green]Tidy complete![/bold green]")


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
