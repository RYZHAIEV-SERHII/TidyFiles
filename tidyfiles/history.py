from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json
import shutil
from loguru import logger


class OperationHistory:
    def __init__(self, history_file: Path):
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.operations: List[Dict[str, Any]] = []
        self._load_history()
        # Ensure file exists even if empty
        if not self.history_file.exists():
            self._save_history()

    def _load_history(self):
        """Load operation history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    self.operations = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Failed to load history file, starting fresh")
                self.operations = []

    def _save_history(self):
        """Save operation history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.operations, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def add_operation(
        self,
        operation_type: str,
        source: Path,
        destination: Path,
        timestamp: datetime = None,
    ):
        """Add a new operation to history."""
        if timestamp is None:
            timestamp = datetime.now()

        operation = {
            "type": operation_type,
            "source": str(source),
            "destination": str(destination),
            "timestamp": timestamp.isoformat(),
            "status": "completed",
        }
        self.operations.append(operation)
        self._save_history()

    def undo_last_operation(self) -> bool:
        """Undo the last operation in history."""
        if not self.operations:
            return False

        last_operation = self.operations[-1]
        try:
            source = Path(last_operation["source"])
            destination = Path(last_operation["destination"])

            if last_operation["type"] == "move":
                # Move file back to original location
                if destination.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(source))
                    logger.info(f"Undid move operation: {destination} -> {source}")
                else:
                    logger.warning(f"Destination file no longer exists: {destination}")
                    return False

            elif last_operation["type"] == "delete":
                # Restore deleted directory
                if not source.exists():
                    source.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Restored deleted directory: {source}")
                else:
                    logger.warning(f"Directory already exists: {source}")
                    return False

            last_operation["status"] = "undone"
            self._save_history()
            return True

        except Exception as e:
            logger.error(f"Failed to undo operation: {e}")
            return False

    def get_last_operation(self) -> Dict[str, Any]:
        """Get the last operation from history."""
        return self.operations[-1] if self.operations else None

    def clear_history(self):
        """Clear all operation history."""
        self.operations = []
        self._save_history()
