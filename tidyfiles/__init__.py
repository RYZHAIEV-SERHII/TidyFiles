"""TidyFiles is a user-friendly, lightweight CLI tool designed to bring order to your Downloads (or any other) folder!
It intelligently organizes files by type and keep logs of all the sorting magic."""

__version__ = "0.6.13-rc.1"

from tidyfiles.cli import app

__all__ = ["app"]
