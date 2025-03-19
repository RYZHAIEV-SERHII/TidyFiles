# TidyFiles

![TidyFiles Logo](https://i.imgur.com/VkDL4QU.jpeg)

[![PyPI version](https://badge.fury.io/py/tidyfiles.svg)](https://badge.fury.io/py/tidyfiles)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/RYZHAIEV-SERHII/TidyFiles/workflows/tests/badge.svg)](https://github.com/RYZHAIEV-SERHII/TidyFiles/actions)

**TidyFiles** is a user-friendly, lightweight CLI tool designed to bring order to your Downloads (or any other) folder! It intelligently organizes files by type and keeps logs of all the sorting magic.

## 🌟 Features
- **Smart Organization**: Automatically categorizes files by type (images, documents, videos, etc.)
- **Dry Run Mode**: Preview changes with `--dry-run` before actual organization
- **Flexible Configuration**: Customize source and destination directories
- **Detailed Logging**: Track all operations with console and file logging
- **Rich CLI Interface**: Beautiful command-line interface with progress indicators
- **Safe Operations**: Maintains file integrity during organization

## 🔧 Tech Stack
- **Python 3.13+**: Modern Python features for robust performance
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

### Coming Soon (v0.2.0)
- [ ] `--lang` flag for multi-language support
- [ ] `--undo` operation to reverse recent changes
- [ ] Custom file category definitions
- [ ] Subdirectory organization support

### Future Plans (v0.3.0+)
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
- **Latest Version**: 0.1.0
- **Python Compatibility**: 3.13+
- **Platform Support**: Windows, macOS, Linux

#### Created with ❤️ by Serhii Ryzhaiev
