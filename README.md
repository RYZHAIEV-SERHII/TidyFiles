# TidyFiles

![TidyFiles Logo](https://i.imgur.com/VkDL4QU.jpeg)

[![PyPI - Version](https://img.shields.io/pypi/v/tidyfiles)](https://pypi.org/project/tidyfiles/)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/RYZHAIEV-SERHII/TidyFiles/branch/main/graph/badge.svg)](https://codecov.io/gh/RYZHAIEV-SERHII/TidyFiles)
[![Tests](https://github.com/RYZHAIEV-SERHII/TidyFiles/actions/workflows/tests.yml/badge.svg)](https://github.com/RYZHAIEV-SERHII/TidyFiles/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat&logo=github)](CONTRIBUTING.md)

**TidyFiles** is a user-friendly, lightweight CLI tool designed to bring order to your Downloads (or any other) folder!
It intelligently organizes files by type and keeps logs of all the sorting magic.

## 🌟 Features

- **Smart Organization**: Automatically categorizes files by type (images, documents, videos, etc.)
- **Operation History**: Track and manage all file operations with detailed history
    - View session history with source and destination directories
    - Filter history by session ID or limit number of entries
    - Detailed operation logs with timestamps and status
- **Undo Support**: Revert specific operations or entire sessions safely
    - Undo individual file moves or directory deletions
    - Revert entire sessions with a single command
    - Independent operation handling - undo specific files without affecting others
    - Operation status tracking (completed, partially_undone, undone)
- **Session Management**: Track operations by session with detailed status information
    - Group operations by session for better organization
    - Track session status and completion
    - View session details including source/destination paths
- **Dry Run Mode**: Preview changes with `--dry-run` before actual organization
- **Flexible Configuration**: Customize source and destination directories
- **Detailed Logging**: Track all operations with console and file logging
- **Rich CLI Interface**: Beautiful command-line interface with progress indicators
- **Safe Operations**: Maintains file integrity during organization

## 🔧 Tech Stack

- **Core Dependencies**
    - Python >=3.10: Modern Python features
    - Typer: Elegant CLI interface
    - Rich: Beautiful terminal formatting
    - Loguru: Advanced logging
    - Click: CLI framework (Typer dependency)

- **Development Tools**
    - Ruff: Fast Python linter and formatter
    - Pre-commit: Automated code quality checks
    - Semantic Release: Automated versioning

- **Testing Framework**
    - PyTest: Comprehensive test coverage
    - Coverage reporting: Detailed test coverage analysis

## 🚀 Getting Started

### Installation

```bash
pip install tidyfiles
```

### Basic Usage

```bash
# Organize files in a specific directory
tidyfiles --source-dir /path/to/your/folder

# Undo last session if something went wrong
tidyfiles undo
```

### Advanced Usage

* ###### Dry run to preview changes

```bash
tidyfiles --source-dir ~/Downloads --dry-run
```

* ###### Specify custom destination

```bash
tidyfiles --source-dir ~/Downloads --destination-dir ~/Organized
```

* ###### Custom logging

```bash
tidyfiles --source-dir ~/Downloads --log-console-level DEBUG
```

* ###### View operation history (last 10 sessions)

```bash
tidyfiles history
```

* ###### View more history entries

```bash
tidyfiles history --limit 20
```

* ###### View detailed session information

```bash
tidyfiles history --session 3
```

* ###### Undo entire specific session

```bash
tidyfiles undo --session 3
```

* ###### Undo specific operation in a session

```bash
tidyfiles undo --session 3 --number 2
```

## 📁 Example Usage

### Initial State

```plaintext
Downloads/
├── photo1.jpg
├── document.pdf
├── video.mp4
├── photo2.jpg
└── archive.zip
```

### After Organization

```plaintext
Downloads/
├── images/
│   ├── photo1.jpg
│   └── photo2.jpg
├── documents/
│   └── document.pdf
├── videos/
│   └── video.mp4
└── archives/
    └── archive.zip
```

### View History

```bash
$ tidyfiles history --limit 3
                                    Operation Sessions
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Session ID ┃ Date       ┃ Time     ┃ Source           ┃ Destination     ┃ Operations ┃ Status      ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│          3 │ 2025-04-04 │ 00:35:48 │ ~/Downloads      │ ~/Organized     │          5 │ completed   │
│          2 │ 2025-04-04 │ 00:34:12 │ ~/Documents      │ ~/Organized     │          3 │ completed   │
│          1 │ 2025-04-04 │ 00:32:05 │ ~/Desktop        │ ~/Organized     │          2 │ completed   │
└────────────┴────────────┴──────────┴──────────────────┴─────────────────┴────────────┴─────────────┘

```

### View detailed session information

```bash
$ tidyfiles history --session 3

Session Details
Started: 2025-04-04 00:35:48
Source: ~/Downloads
Destination: ~/Organized
Status: completed
Operations: 5
                                    Session 3 Operations
┏━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ # ┃ Time     ┃ Type ┃ Source                        ┃ Destination                             ┃ Status    ┃
┡━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1 │ 00:35:48 │ move │ ~/Downloads/document.pdf      │ ~/Organized/documents/document.pdf      │ completed │
│ 2 │ 00:35:48 │ move │ ~/Downloads/photo1.jpg        │ ~/Organized/images/photo1.jpg           │ completed │
│ 3 │ 00:35:48 │ move │ ~/Downloads/photo2.jpg        │ ~/Organized/images/photo2.jpg           │ completed │
│ 4 │ 00:35:48 │ move │ ~/Downloads/video.mp4         │ ~/Organized/videos/video.mp4            │ completed │
│ 5 │ 00:35:48 │ move │ ~/Downloads/archive.zip       │ ~/Organized/archives/archive.zip        │ completed │
└───┴──────────┴──────┴───────────────────────────────┴─────────────────────────────────────────┴───────────┘

```

### Undo specific session

```bash
$ tidyfiles undo --session 3
Do you want to undo all operations in this session? [y/N]: y
✔ Successfully undone all operations in session 3

```

### Undo specific operation

```bash
$ tidyfiles undo --session 3 --number 2
Do you want to undo operation 2 (~/Downloads/photo1.jpg -> ~/Organized/images/photo1.jpg)? [y/N]: y
✔ Successfully undone operation 2 in session 3
```

## 📋 Logging and History

TidyFiles maintains comprehensive logs and history:

### Console Output

- Real-time operation progress
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Rich formatting with colors and icons
- Operation summaries and confirmations

### File Logs

- Detailed operation logs in `~/.tidyfiles/tidyfiles.log`
- Session history in `~/.tidyfiles/history.json`
- Persistent across program restarts
- Human-readable format for easy debugging

## 🧰️ Contributing

We welcome contributions! Check out our [Contributing Guidelines](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🎯 Future Roadmap (v0.8.0+)

- 🛈 **Info Feature Expansion**: Enhance the info feature to provide detailed metadata and file information.
- 🌐 **Multi-language Interface**: Switch between different languages using `--lang` flag for global accessibility.
- 📁 **Custom Categories**: Define your own file categories and organization rules via simple configuration.
- 🗂️ **Smart Subdirectories**: Create dynamic folder structures based on file metadata and patterns.
- 🔍 **Smart Deduplication**: Intelligently detect and handle duplicate files while preserving the newest versions.
- ✨ **Advanced Renaming**: Bulk rename files using patterns, dates, and custom templates.
- 🤖 **AI Organization**: Use AI to categorize files based on content, not just extensions.
- 🖥️ **GUI Interface**: Optional graphical interface for users who prefer visual file management.
- ☁️ **Cloud Integration**: Direct organization of Dropbox and Google Drive folders.
- ⏰ **Scheduled Tasks**: Set up automatic organization at specified times or intervals.
- 🗜️ **Smart Compression**: Automatically compress old or large files to save space.
- 📊 **Organization Presets**: Save and share your favorite organization patterns.
- 📈 **Usage Analytics**: Track space savings and organization patterns over time.
- 🔄 **Silent Updates**: Seamless background updates with rollback support.
- 🎨 **Terminal Themes**: Customize CLI appearance with modern color schemes.
- 🔔 **Smart Notifications**: Get notified when long-running operations complete.
- 📱 **Remote Control**: Monitor and manage operations from your mobile device.

For detailed version history and latest changes, see our [CHANGELOG](CHANGELOG.md) 📈

## 📊 Stats

- **First Release**: March 2025
- **Latest Version**: [![PyPI version](https://badge.fury.io/py/tidyfiles.svg)](https://badge.fury.io/py/tidyfiles)
- **Python Compatibility**: [![Python 3.10-3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
- **Platform Support**: Windows, macOS, Linux

### Created with ❤️ by Serhii Ryzhaiev
