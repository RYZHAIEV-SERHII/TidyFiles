# TidyFiles

![TidyFiles Logo](https://i.imgur.com/VkDL4QU.jpeg)

[![PyPI version](https://badge.fury.io/py/tidyfiles.svg)](https://badge.fury.io/py/tidyfiles)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/RYZHAIEV-SERHII/TidyFiles)](https://github.com/RYZHAIEV-SERHII/TidyFiles/releases)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/RYZHAIEV-SERHII/TidyFiles/branch/main/graph/badge.svg)](https://codecov.io/gh/RYZHAIEV-SERHII/TidyFiles)
[![Tests](https://github.com/RYZHAIEV-SERHII/TidyFiles/workflows/tests/badge.svg)](https://github.com/RYZHAIEV-SERHII/TidyFiles/actions)
[![GitHub last commit](https://img.shields.io/github/last-commit/RYZHAIEV-SERHII/TidyFiles)](https://github.com/RYZHAIEV-SERHII/TidyFiles/commits)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TidyFiles** is a user-friendly, lightweight CLI tool designed to bring order to your Downloads (or any other) folder! It intelligently organizes files by type and keeps logs of all the sorting magic.

## 🌟 Features
- **Smart Organization**: Automatically categorizes files by type (images, documents, videos, etc.)
- **Dry Run Mode**: Preview changes with `--dry-run` before actual organization
- **Flexible Configuration**: Customize source and destination directories
- **Detailed Logging**: Track all operations with console and file logging
- **Rich CLI Interface**: Beautiful command-line interface with progress indicators
- **Safe Operations**: Maintains file integrity during organization

## 🔧 Tech Stack
- **Python >=3.10**: Modern Python features for robust performance
- **Typer**: For elegant CLI interface
- **Rich**: Beautiful terminal formatting and output
- **Loguru**: Advanced logging capabilities
- **Ruff**: For code formatting and linting
- **Pre-commit**: Automated code quality checks
- **PyTest**: Comprehensive test coverage

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

## 🎯 Roadmap

### Coming Soon (v0.7.0)
- [ ] `--lang` flag for multi-language support
- [ ] `--undo` operation to reverse recent changes
- [ ] Custom file category definitions
- [ ] Subdirectory organization support

### Future Plans (v0.8.0+)
- [ ] File deduplication detection
- [ ] Bulk rename operations
- [ ] File content-based organization
- [ ] GUI interface option
- [ ] Integration with cloud storage services
- [ ] Schedule automated organization
- [ ] File compression options
- [ ] Organization templates/presets
- [ ] Statistics and reports generation

## 📊 Stats
- **First Release**: March 2025
- **Latest Version**: [![PyPI version](https://badge.fury.io/py/tidyfiles.svg)](https://badge.fury.io/py/tidyfiles)
- **Python Compatibility**: [![Python 3.10-3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
- **Platform Support**: Windows, macOS, Linux

#### Created with ❤️ by Serhii Ryzhaiev
