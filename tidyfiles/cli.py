import typer
import sys
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
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
from loguru import logger

# Global variable to hold the current history instance for signal handlers
_current_history: Optional[OperationHistory] = None


def signal_handler(sig, frame):
    """Handle termination signals to properly close active sessions.

    This function is called when the program receives a termination signal
    (like SIGINT from Ctrl+C). It ensures that any active session is properly
    marked as completed before the program exits.

    Args:
        sig: Signal number
        frame: Current stack frame
    """
    global _current_history

    if _current_history and _current_history.current_session:
        # Mark the current session as completed
        _current_history.current_session["status"] = "completed"
        _current_history._save_history()
        logger.info("Session properly closed due to program termination")

    # Exit with non-zero status for abnormal termination
    sys.exit(1)


# Register signal handlers for common termination signals
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill command

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
    """Show the application version and exit if the --version flag is used."""
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
    clear_history: bool = typer.Option(
        False,
        "--clear-history",
        help="Clear the entire operation history",
    ),
    last_session: bool = typer.Option(
        False,
        "--last-session",
        help="Show details for the last session",
    ),
):
    """Show the history of file organization operations.

    The history is organized into sessions, where each session represents one run of
    the tidyfiles command. By default, shows a list of all sessions with their source
    and destination directories.

    Note: Sessions with 'in_progress' status are automatically fixed during loading
    if all operations in the session are completed.

    Examples:
        View all sessions (latest first):
            $ tidyfiles history

        View only the last 5 sessions:
            $ tidyfiles history --limit 5

        View details of a specific session:
            $ tidyfiles history --session 3

        View details of the last session:
            $ tidyfiles history --last-session

        Clear all history:
            $ tidyfiles history --clear-history

        # Clear the log file:
        #     $ tidyfiles history --clear-log
    """
    if history_file is None:
        history_file_path = get_default_history_file()
    else:
        history_file_path = Path(history_file)

    history = OperationHistory(history_file_path)

    if clear_history:
        if typer.confirm("Are you sure you want to clear the entire history?"):
            history.clear_history()
            console.print("[green]History cleared successfully.[/green]")
        else:
            console.print("[yellow]History clear operation cancelled.[/yellow]")
        return

    if last_session:
        last_sess = history.get_last_session()
        if last_sess:
            session_id = last_sess["id"]
        else:
            console.print(
                "[yellow]No sessions in history to show the last one.[/yellow]"
            )
            return

    sessions = history.sessions[-limit:] if limit > 0 else history.sessions

    if not sessions:
        console.print("[yellow]No sessions in history[/yellow]")
        return

    # Sessions with 'in_progress' status are now automatically fixed during loading

    if session_id is not None:
        try:
            # Show detailed view of a specific session
            session = next((s for s in history.sessions if s["id"] == session_id), None)
            if not session:
                console.print(f"[red]Session {session_id} not found[/red]")
                return

            # Safely get operations with error handling
            try:
                if isinstance(session, dict) and "operations" in session:
                    operations = session["operations"]
                else:
                    operations = []
            except Exception:
                operations = []
                console.print(
                    "[yellow]Warning: Could not access operations data[/yellow]"
                )

            # Safely get session start time
            try:
                if isinstance(session, dict) and "start_time" in session:
                    session_start = datetime.fromisoformat(session["start_time"])
                else:
                    session_start = datetime.now()
            except Exception:
                session_start = datetime.now()
                console.print(
                    "[yellow]Warning: Could not parse session start time[/yellow]"
                )

            # Ensure operations is a list
            if not isinstance(operations, list):
                console.print(
                    "[yellow]Warning: Operations data is corrupted, showing empty list[/yellow]"
                )
                operations = []

            # Safely build session info with error handling
            try:
                source_dir = (
                    session.get("source_dir", "N/A")
                    if isinstance(session, dict)
                    else "N/A"
                )
                dest_dir = (
                    session.get("destination_dir", "N/A")
                    if isinstance(session, dict)
                    else "N/A"
                )
                status = (
                    session.get("status", "unknown")
                    if isinstance(session, dict)
                    else "unknown"
                )

                session_info = (
                    f"\n[bold]Session Details[/bold]\n"
                    f"Started: [magenta]{session_start.strftime('%Y-%m-%d %H:%M:%S')}[/magenta]\n"
                    f"Source: [blue]{source_dir}[/blue]\n"
                    f"Destination: [blue]{dest_dir}[/blue]\n"
                    f"Status: [yellow]{status}[/yellow]\n"
                    f"Operations: [cyan]{len(operations) if isinstance(operations, list) else 0}[/cyan]"
                )
                console.print(session_info)
            except Exception as e:
                console.print(f"[red]Error displaying session info: {str(e)}[/red]")

            # Show operations list or no operations message
            if not operations or not isinstance(operations, list):
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

            try:
                for i, op in enumerate(operations, 1):
                    # Ensure each operation is a dictionary
                    if not isinstance(op, dict):
                        continue

                    # Get operation fields with fallbacks for missing data
                    timestamp_str = op.get("timestamp", datetime.now().isoformat())
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        time_str = timestamp.strftime("%H:%M:%S")
                    except (ValueError, TypeError):
                        time_str = "unknown"

                    table.add_row(
                        str(i),
                        time_str,
                        op.get("type", "unknown"),
                        op.get("source", "unknown"),
                        op.get("destination", "unknown"),
                        op.get("status", "unknown"),
                    )
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error displaying operations: {str(e)}[/red]")
                console.print("[yellow]Session data may be corrupted[/yellow]")
        except Exception as e:
            console.print(f"[red]Error processing session {session_id}: {str(e)}[/red]")
            return

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
    session_id: Optional[int] = typer.Option(
        None,
        "--session",
        "-s",
        help="Session ID to undo operations from",
    ),
    operation_number: Optional[int] = typer.Option(
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
        history_file_path = get_default_history_file()
    else:
        history_file_path = Path(history_file)

    history = OperationHistory(history_file_path)

    if not history.sessions:
        console.print("[yellow]No sessions in history[/yellow]")
        return

    # Determine the target session
    if session_id is None:
        if operation_number is not None:
            console.print(
                "[red]Error: Using --number requires specifying --session.[/red]"
            )
            raise typer.Exit(1)
        else:
            target_session = history.sessions[-1]
            session_id = target_session["id"]
    else:
        target_session = next(
            (s for s in history.sessions if s["id"] == session_id), None
        )
        if not target_session:
            console.print(f"[red]Session {session_id} not found[/red]")
            return

    # Initialize Settings and Logger for the undo command
    settings = get_settings(
        # Pass a placeholder source_dir
        source_dir=".",
        # Logging/settings options are not passed from CLI,
        # so get_settings will use defaults or load from settings file.
    )
    logger = get_logger(**settings)

    operations = target_session["operations"]
    if not operations:
        console.print(f"[yellow]No operations in session {session_id}[/yellow]")
        return

    if operation_number is not None:
        # ---- Undo Specific Operation ----
        if operation_number < 1 or operation_number > len(operations):
            console.print(f"[red]Invalid operation number: {operation_number}[/red]")
            return

        operation = operations[operation_number - 1]

        # Show operation details and confirm
        try:
            op_details = (
                f"Operation to undo:\n"
                f"Session ID: [cyan]{session_id}[/cyan]\n"
                f"Operation #: [cyan]{operation_number}[/cyan]\n"
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

                def run_undo_operation():
                    with Progress(
                        *progress_columns, console=console, transient=True
                    ) as progress:
                        undo_task_id = progress.add_task(
                            "Undoing operation...", total=1
                        )
                        progress_bar: ProgressBarProtocol = progress  # type: ignore
                        if history.undo_operation(
                            session_id,
                            operation_number - 1,
                            progress_bar,
                            undo_task_id,
                            logger=logger,
                        ):
                            console.print(
                                "[green]Operation successfully undone![/green]"
                            )
                        else:
                            console.print("[red]Failed to undo operation[/red]")

                logger.info(
                    f"--- Undo Operation {operation_number} in Session {session_id} started ---"
                )
                start_undo_op_time = time.time()
                run_undo_operation()
                end_undo_op_time = time.time()
                undo_op_duration = str(
                    timedelta(seconds=int(end_undo_op_time - start_undo_op_time))
                )
                logger.info(
                    f"--- Undo Operation {operation_number} in Session {session_id} ended (Duration: {undo_op_duration}) ---"
                )
            else:
                console.print("[yellow]Operation cancelled[/yellow]")

        except Exception as e:
            console.print(
                f"[red]Error processing undo for operation {operation_number}: {e}[/red]"
            )
            console.print(
                "[yellow]Operation may be corrupt or could not be undone.[/yellow]"
            )
            raise typer.Exit(1)

    else:
        # ---- Undo Entire Session ----
        session_start = datetime.fromisoformat(target_session["start_time"])
        console.print(
            Panel(
                f"Session to undo:\n"
                f"Session ID: [cyan]{target_session['id']}[/cyan]\n"
                f"Started: [magenta]{session_start.strftime('%Y-%m-%d %H:%M:%S')}[/magenta]\n"
                f"Operations: [blue]{len(operations)}[/blue]\n"
                f"Status: [yellow]{target_session['status']}[/yellow]",
                title="[bold cyan]Undo Entire Session[/bold cyan]",
                expand=False,
            )
        )

        if typer.confirm("Do you want to undo all operations in this session?"):
            progress_columns = [
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                TimeElapsedColumn(),
            ]

            def run_undo_operations():
                nonlocal success  # Define success for this scope
                success = True
                with Progress(
                    *progress_columns, console=console, transient=True
                ) as progress:
                    undo_task_id = progress.add_task(
                        "Undoing operations...", total=len(operations)
                    )
                    for i in reversed(range(len(operations))):
                        progress_bar: ProgressBarProtocol = progress  # type: ignore
                        if not history.undo_operation(
                            session_id, i, progress_bar, undo_task_id, logger=logger
                        ):
                            console.print("[red]Failed to undo all operations[/red]")
                            success = False
                            break

            success = True  # Initialize success before calling run_undo_operations
            logger.info(f"--- Undo Session {session_id} started ---")
            start_undo_time = time.time()
            run_undo_operations()
            end_undo_time = time.time()
            undo_duration = str(timedelta(seconds=int(end_undo_time - start_undo_time)))
            logger.info(
                f"--- Undo Session {session_id} ended (Duration: {undo_duration}) ---"
            )

            if success:
                console.print(
                    "[green]All operations in session successfully undone![/green]"
                )
        else:
            console.print("[yellow]Operation cancelled[/yellow]")
            return


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
        False, "--dry-run", help="Run in dry-run mode (no actual changes)"
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
    clear_log: bool = typer.Option(
        False,
        "--clear-log",
        help="Clear the log file and exit.",
        is_eager=True,  # Process this before other options/commands
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
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the application version and exit.",
    ),
):
    """TidyFiles - Organize your files automatically by type."""
    # Handle --clear-log flag first, as it's an independent action
    if clear_log:
        # Determine log file path using default settings
        log_folder = Path(DEFAULT_SETTINGS["log_folder_name"])
        log_file = log_folder / DEFAULT_SETTINGS["log_file_name"]

        if typer.confirm(
            f"Are you sure you want to delete the log file at '{log_file}'?"
        ):
            try:
                log_file.unlink(missing_ok=True)
                console.print(
                    f"[green]Log file '{log_file}' deleted successfully.[/green]"
                )
            except OSError as e:
                console.print(f"[red]Error deleting log file: {e}[/red]")
                raise typer.Exit(1)  # Exit with error if deletion fails
        else:
            console.print("[yellow]Log file deletion cancelled.[/yellow]")
        raise typer.Exit(0)  # Exit after handling the flag

    # If no source_dir and no command is being executed (and --clear-log wasn't used),
    # show help.
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
        session_id = None  # Initialize session_id
        if not dry_run:
            history_file_path = (
                Path(history_file) if history_file else get_default_history_file()
            )
            history = OperationHistory(history_file_path)

            # Set global history for signal handlers
            _current_history = history

            # Start a new session for this organization run
            history.start_session(
                source_dir=settings["source_dir"],
                destination_dir=settings["destination_dir"],
            )
            session_id = history.current_session["id"]
            logger.info(f"--- Session {session_id} started ---")

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

        # Execute the function
        run_file_operations()

        # Record end time and calculate duration
        end_time = time.time()
        duration = end_time - start_time
        duration_str = str(timedelta(seconds=int(duration)))

        if not dry_run and session_id is not None:
            logger.info(
                f"--- Session {session_id} ended (Duration: {duration_str}) ---"
            )

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
                history.current_session["status"] = "completed"
                history._save_history()

            # Clear global history reference since we're done
            _current_history = None

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
