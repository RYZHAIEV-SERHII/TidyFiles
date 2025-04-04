from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json
import shutil
from loguru import logger


class OperationHistory:
    """Class for managing operation history."""

    def __init__(self, history_file: Path):
        """Initialize history manager.

        Args:
            history_file: Path to history file
        """
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: List[Dict[str, Any]] = []
        self.current_session = None
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
        """Load operation history from file."""
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
                else:
                    self.sessions = []
            except json.JSONDecodeError:
                logger.warning("Failed to load history file, starting fresh")
                self.sessions = []

    def _save_history(self):
        """Save operation history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def start_session(self, source_dir: Path = None, destination_dir: Path = None):
        """Start a new session for grouping operations.

        Args:
            source_dir (Path, optional): Source directory for the operations
            destination_dir (Path, optional): Destination directory for the operations
        """
        if self.current_session:
            # Close previous session if it exists
            self.current_session["status"] = "completed"

        # Create new session
        timestamp = datetime.now()
        self.current_session = {
            "id": len(self.sessions) + 1,
            "start_time": timestamp.isoformat(),
            "status": "in_progress",
            "operations": [],
            "source_dir": str(source_dir) if source_dir else None,
            "destination_dir": str(destination_dir) if destination_dir else None,
        }
        # Don't convert None to 'None' string
        if self.current_session["source_dir"] == "None":
            self.current_session["source_dir"] = None
        if self.current_session["destination_dir"] == "None":
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
        if not self.current_session:
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

    def undo_operation(self, session_id: int, operation_idx: int = None) -> bool:
        """Undo a specific operation or the last operation in a session.

        Args:
            session_id: ID of the session containing the operation
            operation_idx: Index of the operation to undo (0-based). If None, undoes the last operation.

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

            if operation["type"] not in ["move", "delete"]:
                logger.warning(f"Invalid operation type: {operation['type']}")
                return False

            if operation["type"] == "move":
                # Move file back to original location
                if destination.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(source))
                    logger.info(f"Undid move operation: {destination} -> {source}")
                else:
                    logger.warning(f"Destination file no longer exists: {destination}")
                    return False

            elif operation["type"] == "delete":
                # Restore deleted directory
                if not source.exists():
                    source.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Restored deleted directory: {source}")
                else:
                    logger.warning(f"Directory already exists: {source}")
                    return False

            operation["status"] = "undone"

            # Update session status based on its operations
            if all(op["status"] == "undone" for op in operations):
                session["status"] = "undone"
            else:
                session["status"] = "partially_undone"

            self._save_history()
            return True

        except Exception as e:
            logger.error(f"Failed to undo operation: {e}")
            return False

    def undo_last_operation(self) -> bool:
        """Undo the last operation in the most recent session."""
        if not self.sessions:
            return False
        return self.undo_operation(self.sessions[-1]["id"])

    def get_last_operation(self) -> Dict[str, Any]:
        """Get the last operation from history."""
        if not self.sessions or not self.sessions[-1]["operations"]:
            return None
        return self.sessions[-1]["operations"][-1]

    def clear_history(self):
        """Clear all operation history."""
        self.sessions = []
        self.current_session = None
        self._save_history()

    def get_last_session(self):
        """Get the most recent session."""
        return self.sessions[-1] if self.sessions else None
