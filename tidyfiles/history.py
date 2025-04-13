from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, TypedDict
import json
import shutil
from loguru import logger


class SessionDict(TypedDict, total=False):
    """TypedDict for session structure in the operation history.

    Attributes:
        id: Unique identifier for the session
        start_time: ISO format timestamp when the session started
        status: Current status of the session (e.g., "in_progress", "completed")
        operations: List of operations performed in this session
        source_dir: Source directory for the operations in this session
        destination_dir: Destination directory for the operations in this session

    Note:
        Using total=False to make all fields optional
    """

    id: int
    start_time: str
    status: str
    operations: List[Dict[str, Any]]
    source_dir: Optional[str]
    destination_dir: Optional[str]


class OperationHistory:
    """Manages the history of file operations (move, delete) across multiple sessions.

    This class handles loading, saving, and modifying the operation history stored
    in a JSON file. It organizes operations into sessions, where each session
    corresponds to a single run of the tidyfiles command.

    Key functionalities include:
    - Starting and managing sessions.
    - Adding individual file operations (move, delete) to the current session.
    - Loading history from a file, including handling older formats and recovering
      incomplete sessions.
    - Saving the history back to the file.
    - Undoing specific operations or entire sessions.
    - Clearing the entire history.
    - Retrieving the last session.

    Attributes:
        history_file (Path): The path to the JSON file where the history is stored.
        sessions (List[SessionDict]): A list of all past sessions, loaded from the history file.
        current_session (Optional[SessionDict]): The currently active session, or None.
    """

    def __init__(self, history_file: Path):
        """Initialize history manager.

        Args:
            history_file: Path to history file
        """
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: List[SessionDict] = []
        self.current_session: Optional[SessionDict] = None
        self._load_history()
        # Ensure file exists even if empty
        if not self.history_file.exists():
            self._save_history()

    @property
    def operations(self):
        """Get all operations from all sessions as a flat list.
        This property maintains backward compatibility with tests.
        """
        all_operations = []
        for session in self.sessions:
            all_operations.extend(session["operations"])
        return all_operations

    def _load_history(self):
        """Load operation history from file.

        This method also automatically recovers any sessions that might have been
        left in the 'in_progress' state due to unexpected program termination.
        """
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    data = json.load(f)

                # Handle old format (flat list of operations)
                if (
                    data
                    and isinstance(data, list)
                    and all(isinstance(op, dict) for op in data)
                    and not any("operations" in op for op in data)  # Skip if new format
                ):
                    # Convert old format to new session-based format
                    # Ensure each operation has required fields
                    now = datetime.now().isoformat()
                    for op in data:
                        if "timestamp" not in op:
                            op["timestamp"] = now
                        if "type" not in op:
                            # Determine type based on whether source and destination are the same
                            op["type"] = (
                                "delete"
                                if op.get("source") == op.get("destination")
                                else "move"
                            )
                        if "status" not in op:
                            op["status"] = "completed"
                        if "source" not in op:
                            op["source"] = "unknown"
                        if "destination" not in op:
                            op["destination"] = op["source"]

                    self.sessions = [
                        {
                            "id": 1,
                            "start_time": data[0].get("timestamp", now)
                            if data
                            else now,
                            "operations": data,
                            "status": "completed",
                            "source_dir": None,
                            "destination_dir": None,
                        }
                    ]
                elif isinstance(data, list):
                    self.sessions = data

                    # Auto-recover any sessions left in 'in_progress' state
                    # This handles cases where the program was terminated unexpectedly
                    recovery_needed = False
                    for session in self.sessions:
                        if session.get("status", "").lower() == "in_progress":
                            # Check if all operations are completed
                            operations = session.get("operations", [])
                            if operations and all(
                                op.get("status") == "completed" for op in operations
                            ):
                                # If all operations are completed, mark the session as completed
                                session["status"] = "completed"
                                recovery_needed = True
                                logger.info(
                                    f"Auto-recovered session {session.get('id')} from 'in_progress' to 'completed'"
                                )

                    # Save the changes if we made any recoveries
                    if recovery_needed:
                        self._save_history()
                else:
                    self.sessions = []
            except json.JSONDecodeError:
                logger.warning("Failed to load history file, starting fresh")
                self.sessions = []

    def _save_history(self):
        """Save operation history to file.

        The history is saved in JSON format to the file at the specified path.
        If the file does not exist, it is created. If the file exists, it is overwritten.
        The JSON is formatted with indentation for better readability.

        The method ensures the parent directory exists before attempting to write the file.
        Any exceptions during the save operation are logged but not raised.
        """
        try:
            # Ensure the parent directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            # Write directly to file using json.dumps for better formatting
            with open(self.history_file, "w") as f:
                f.write(json.dumps(self.sessions, indent=2))

        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def start_session(self, source_dir: Path = None, destination_dir: Path = None):
        """Start a new session for grouping operations.

        Args:
            source_dir (Path, optional): Source directory for the operations
            destination_dir (Path, optional): Destination directory for the operations
        """
        if self.current_session is not None:
            # Close previous session if it exists
            self.current_session["status"] = "completed"

        # Create new session
        timestamp = datetime.now()
        # Create new session with proper typing
        new_session: SessionDict = {
            "id": len(self.sessions) + 1,
            "start_time": timestamp.isoformat(),
            "status": "in_progress",
            "operations": [],
            "source_dir": str(source_dir) if source_dir else None,
            "destination_dir": str(destination_dir) if destination_dir else None,
        }
        self.current_session = new_session
        # Don't convert None to 'None' string
        if self.current_session is not None:
            if self.current_session.get("source_dir") == "None":
                self.current_session["source_dir"] = None
            if self.current_session.get("destination_dir") == "None":
                self.current_session["destination_dir"] = None
        self.sessions.append(self.current_session)
        self._save_history()
        return self.current_session["id"]

    def add_operation(
        self,
        operation_type: str,
        source: Path,
        destination: Path,
        timestamp: datetime = None,
    ):
        """Add new operation to history.

        Args:
            operation_type: Type of operation (move/delete)
            source: Source path
            destination: Destination path
            timestamp: Optional timestamp for the operation
        """
        if self.current_session is None:
            self.start_session(source.parent, destination.parent)

        if timestamp is None:
            timestamp = datetime.now()

        operation = {
            "type": operation_type,
            "source": str(source),
            "destination": str(destination),
            "timestamp": timestamp.isoformat()
            if isinstance(timestamp, datetime)
            else timestamp,
            "status": "completed",
        }
        self.current_session["operations"].append(operation)
        self._save_history()

    def undo_operation(
        self,
        session_id: int,
        operation_idx: int = None,
        progress=None,
        task_id=None,
        logger: Optional[logger] = None,
    ) -> bool:
        """Undo a specific operation or the last operation in a session.

        Args:
            session_id: ID of the session containing the operation
            operation_idx: Index of the operation to undo (0-based). If None, undoes the last operation.
            progress (Progress, optional): Rich progress bar instance for displaying progress.
            task_id (int, optional): Task ID for the progress bar.
            logger (Optional[logger]): Logger instance for logging undo actions.

        Returns:
            bool: True if operation was successfully undone, False otherwise
        """
        # Find the session
        session = next((s for s in self.sessions if s["id"] == session_id), None)
        if not session or not session["operations"]:
            return False

        # Get the operation to undo
        operations = session["operations"]
        if operation_idx is not None:
            if operation_idx < 0 or operation_idx >= len(operations):
                return False
            operation = operations[operation_idx]
        else:
            operation = operations[-1]

        # Don't undo if already undone
        if operation["status"] == "undone":
            return False

        try:
            source = Path(operation["source"])
            destination = Path(operation["destination"])

            # Update progress bar description if available
            if progress and task_id is not None:
                progress.update(
                    task_id,
                    advance=0,
                    description=f"Undoing: {Path(operation['source']).name}",
                )

            if operation["type"] not in ["move", "delete"]:
                logger.warning(f"Invalid operation type: {operation['type']}")
                return False

            if operation["type"] == "move":
                # Move file back to original location
                if destination.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(source))
                    logger.info(f"UNDO MOVE | FROM: {destination} | TO: {source}")
                else:
                    logger.warning(
                        f"UNDO MOVE [SKIP] | Destination file no longer exists: {destination}"
                    )
                    # Do not return False, allow marking as undone even if file is missing
                    # This prevents getting stuck if a file was manually deleted after sorting.

            elif operation["type"] == "delete":
                # Restore deleted directory
                if not source.exists():
                    source.mkdir(parents=True, exist_ok=True)
                    logger.info(f"UNDO DELETE | RESTORED: {source}")
                else:
                    logger.warning(
                        f"UNDO DELETE [SKIP] | Directory already exists: {source}"
                    )
                    # Do not return False, allow marking as undone if dir exists

            operation["status"] = "undone"

            # Update session status based on its operations
            if all(op["status"] == "undone" for op in operations):
                session["status"] = "undone"
            else:
                session["status"] = "partially_undone"

            self._save_history()

            # Advance progress bar if available
            if progress and task_id is not None:
                progress.update(task_id, advance=1)

            return True

        except Exception as e:
            logger.error(f"Failed to undo operation: {e}")
            return False

    def clear_history(self):
        """Clear all operation history."""
        self.sessions = []
        self.current_session = None
        self._save_history()

    def get_last_session(self):
        """Get the most recent session."""
        return self.sessions[-1] if self.sessions else None
