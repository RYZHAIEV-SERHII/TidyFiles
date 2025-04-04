"""TidyFiles is a user-friendly, lightweight CLI tool designed to bring order to your Downloads (or any other) folder!
It intelligently organizes files by type and keep logs of all the sorting magic."""

__version__ = "0.7.0-rc.2"

from tidyfiles.cli import app

__all__ = ["app"]
