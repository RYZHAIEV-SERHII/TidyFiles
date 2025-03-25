# TidyFiles

![TidyFiles Logo](https://i.imgur.com/VkDL4QU.jpeg)

[![PyPI version](https://badge.fury.io/py/tidyfiles.svg)](https://badge.fury.io/py/tidyfiles)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/RYZHAIEV-SERHII/TidyFiles)](https://github.com/RYZHAIEV-SERHII/TidyFiles/releases)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/RYZHAIEV-SERHII/TidyFiles/branch/main/graph/badge.svg)](https://codecov.io/gh/RYZHAIEV-SERHII/TidyFiles)
[![Tests](https://github.com/RYZHAIEV-SERHII/TidyFiles/actions/workflows/tests.yml/badge.svg)](https://github.com/RYZHAIEV-SERHII/TidyFiles/actions)
[![GitHub last commit](https://img.shields.io/github/last-commit/RYZHAIEV-SERHII/TidyFiles)](https://github.com/RYZHAIEV-SERHII/TidyFiles/commits)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat&logo=github)](CONTRIBUTING.md)

**TidyFiles** is a user-friendly, lightweight CLI tool designed to bring order to your Downloads (or any other) folder! It intelligently organizes files by type and keeps logs of all the sorting magic.

## 🌟 Features
- **Smart Organization**: Automatically categorizes files by type (images, documents, videos, etc.)
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
tidyfiles --source-dir /path/to/your/downloads
```

### Advanced Usage
```bash
# Dry run to preview changes
tidyfiles --source-dir ~/Downloads --dry-run

# Specify custom destination
tidyfiles --source-dir ~/Downloads --destination-dir ~/Organized

# Custom logging
tidyfiles --source-dir ~/Downloads --log-console-level DEBUG
```

## 📁 Example Organization
### Before:
```plaintext
Downloads/
├── photo.jpg
├── document.pdf
├── video.mp4
```
### After:
```plaintext
Downloads/
├── images/
│   └── photo.jpg
├── documents/
│   └── document.pdf
├── videos/
│   └── video.mp4
```

## 📝 Logging
TidyFiles generates detailed logs in:
- Console output (configurable level)
- Log file (`~/.tidyfiles/tidyfiles.log`)

## 🛠️ Contributing
We welcome contributions! Check out our [Contributing Guidelines](CONTRIBUTING.md).

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap & Development

### Upcoming Features (v0.7.0)
- 🌐 **Multi-language Interface**: Switch between different languages using `--lang` flag for global accessibility
- ↩️ **Reversible Operations**: Easily undo recent file organizations with `--undo` command
- 📁 **Custom Categories**: Define your own file categories and organization rules via simple configuration
- 🗂️ **Smart Subdirectories**: Create dynamic folder structures based on file metadata and patterns

### Future Roadmap (v0.8.0+)
- 🔍 **Smart Deduplication**: Intelligently detect and handle duplicate files while preserving the newest versions
- ✨ **Advanced Renaming**: Bulk rename files using patterns, dates, and custom templates
- 🤖 **AI Organization**: Use AI to categorize files based on content, not just extensions
- 🖥️ **GUI Interface**: Optional graphical interface for users who prefer visual file management
- ☁️ **Cloud Integration**: Direct organization of Dropbox and Google Drive folders
- ⏰ **Scheduled Tasks**: Set up automatic organization at specified times or intervals
- 🗜️ **Smart Compression**: Automatically compress old or large files to save space
- 📊 **Organization Presets**: Save and share your favorite organization patterns
- 📈 **Usage Analytics**: Track space savings and organization patterns over time
- 🔄 **Silent Updates**: Seamless background updates with rollback support
- 💾 **History System**: Browse and restore previous file organizations
- 🎨 **Terminal Themes**: Customize CLI appearance with modern color schemes
- 🔔 **Smart Notifications**: Get notified when long-running operations complete
- ⚡ **Reliable Processing**: Resume interrupted operations where they left off
- 🔐 **Safety Checks**: Verify file integrity before and after operations
- 📱 **Remote Control**: Monitor and manage operations from your mobile device

For detailed version history and latest changes, see our [CHANGELOG](CHANGELOG.md) 📈

## 📊 Stats
- **First Release**: March 2025
- **Latest Version**: [![PyPI version](https://badge.fury.io/py/tidyfiles.svg)](https://badge.fury.io/py/tidyfiles)
- **Python Compatibility**: [![Python 3.10-3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
- **Platform Support**: Windows, macOS, Linux

#### Created with ❤️ by Serhii Ryzhaiev
