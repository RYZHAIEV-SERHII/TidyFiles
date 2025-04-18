import os
import sys
from pathlib import Path
from typing import Set, Tuple

from loguru import logger


class SystemSecurity:
    """Security checks for system directories and file operations."""

    @staticmethod
    def get_windows_system_paths() -> Set[Path]:
        """Get Windows system paths that should be protected."""
        system_drive = os.environ.get("SystemDrive", "C:")
        return {
            # Core system directories
            Path(f"{system_drive}/Boot"),
            Path(f"{system_drive}/ProgramData"),
            Path(f"{system_drive}/Program Files"),
            Path(f"{system_drive}/Program Files (x86)"),
            Path(f"{system_drive}/Recovery"),
            Path(f"{system_drive}/System Volume Information"),
            Path(f"{system_drive}/Windows"),
            # Special system directories
            Path(f"{system_drive}/$Recycle.Bin"),
            Path(f"{system_drive}/Documents and Settings"),  # Legacy
            Path(f"{system_drive}/Users/All Users"),
            Path(f"{system_drive}/Users/Default"),
            Path(f"{system_drive}/Users/Public"),
        }

    @staticmethod
    def get_linux_system_paths() -> Set[Path]:
        """Get Linux system paths that should be protected."""
        return {
            # Root-level system directories
            Path("/bin"),
            Path("/boot"),
            Path("/dev"),
            Path("/etc"),
            Path("/lib"),
            Path("/lib32"),
            Path("/lib64"),
            Path("/lost+found"),
            Path("/opt"),
            Path("/proc"),
            Path("/root"),
            Path("/run"),
            Path("/sbin"),
            Path("/srv"),
            Path("/sys"),
            Path("/usr"),
            Path("/var"),
            # Mount points
            Path("/media"),
            Path("/mnt"),
            # Package management
            Path("/snap"),
        }

    @staticmethod
    def get_macos_system_paths() -> Set[Path]:
        """Get macOS system paths that should be protected."""
        return {
            # Core system directories
            Path("/Applications"),
            Path("/Library"),
            Path("/Network"),
            Path("/System"),
            Path("/Users/Guest"),
            Path("/Users/Shared"),
            Path("/bin"),
            Path("/cores"),
            Path("/dev"),
            Path("/opt"),
            Path("/private"),
            Path("/sbin"),
            Path("/usr"),
            Path("/var"),
            # Hidden system directories
            Path("/.fseventsd"),
            Path("/.Spotlight-V100"),
            Path("/.DocumentRevisions-V100"),
        }

    @classmethod
    def get_system_paths(cls) -> Set[Path]:
        """Get system-critical paths based on the current operating system."""
        if sys.platform == "win32":
            return cls.get_windows_system_paths()
        elif sys.platform == "darwin":
            return cls.get_macos_system_paths()
        else:  # Assume Linux/Unix
            return cls.get_linux_system_paths()

    @classmethod
    def is_system_path(cls, path: Path) -> bool:
        """
        Check if the given path is a system path or within a system directory.

        Args:
            path (Path): The path to check.

        Returns:
            bool: True if the path is a system path, False otherwise.
        """
        try:
            path = path.resolve()
            system_paths = cls.get_system_paths()

            # Check if the path is a system path or is a subdirectory of a system path
            return any(
                path == sys_path or path.is_relative_to(sys_path)
                for sys_path in system_paths
            )
        except (OSError, RuntimeError) as e:
            logger.warning(f"Failed to resolve path {path}: {str(e)}")
            return True

    @classmethod
    def is_safe_path(cls, path: Path) -> Tuple[bool, str]:
        """
        Validate if it's safe to perform operations on the given path.

        Args:
            path (Path): The path to validate.

        Returns:
            Tuple[bool, str]: (is_safe, reason_if_unsafe)
        """
        try:
            # Check if path is a system path
            if cls.is_system_path(path):
                msg = f"Operation blocked: {path} is a system directory"
                logger.warning(msg)
                return False, msg

            # Check parent directory permissions first
            parent = path.parent
            if parent.exists() and not os.access(parent, os.W_OK):
                msg = f"Operation blocked: Parent directory {parent} is not writable"
                logger.warning(msg)
                return False, msg

            # Check if path exists and is not writable
            if path.exists():
                if not os.access(path, os.W_OK):
                    msg = f"Operation blocked: {path} is not writable"
                    logger.warning(msg)
                    return False, msg

                # Additional check for macOS hidden system files
                if sys.platform == "darwin" and path.name.startswith("._"):
                    msg = f"Operation blocked: {path} is a macOS system file"
                    logger.warning(msg)
                    return False, msg

                # Check for Windows special files
                if sys.platform == "win32" and path.name.startswith("~"):
                    msg = f"Operation blocked: {path} is a Windows special file"
                    logger.warning(msg)
                    return False, msg

            logger.debug(f"Path {path} is safe")
            return True, ""

        except Exception as e:
            msg = f"Operation blocked: Unable to verify path safety: {str(e)}"
            logger.error(msg)
            return False, msg

    @classmethod
    def validate_path(cls, path: Path, raise_error: bool = True) -> None:
        """
        Validate a path and raise an exception if it's not safe.

        Args:
            path (Path): The path to validate.
            raise_error (bool): Whether to raise an exception on unsafe paths.

        Raises:
            ValueError: If the path is not safe and raise_error is True.
        """
        is_safe, reason = cls.is_safe_path(path)
        if not is_safe and raise_error:
            raise ValueError(reason)
