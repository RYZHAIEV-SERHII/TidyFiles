# `Architecture Overview`

---

## 📁 Project Structure

```plaintext
.
├── .github/                   # GitHub specific configurations
│   ├── workflows/            # CI/CD workflows
│   │   ├── release.yaml     # Release automation workflow
│   │   └── tests.yml       # Testing workflow
│   └── codecov.yml         # CodeCov configuration
│
├── .hooks/                   # Custom Git hooks
│   ├── commit-msg          # Commit message validation script
│   └── hooks-README.md     # Hooks documentation
│
├── tidyfiles/               # Main package directory
│   ├── __init__.py         # Version and package info
│   ├── cli.py              # Command-line interface using Typer
│   ├── config.py           # Configuration handling
│   ├── history.py          # Operation history and session management
│   ├── logger.py           # Logging setup using Loguru
│   └── operations.py       # Core file operations and business logic
│
├── tests/                  # Test suite directory
│   ├── __init__.py
│   ├── conftest.py        # pytest configuration and fixtures
│   ├── test_cli.py        # CLI tests
│   ├── test_config.py     # Configuration tests
│   ├── test_logger.py     # Logger tests
│   └── test_operations.py # Operations tests
│
├── docs/                   # Documentation directory
│   ├── internal/          # Internal documentation
│   │   ├── ARCHITECTURE.md    # This file - architecture overview
│   │   ├── DEVELOPMENT.md     # Development setup and guidelines
│   │   └── RELEASE_WORKFLOW.md # Release process documentation
│   └── README.md          # Documentation overview
│
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── pyproject.toml         # Project configuration and dependencies
├── ruff.toml             # Ruff linter configuration
├── CHANGELOG.md          # Project changelog
├── CODE_OF_CONDUCT.md    # Project code of conduct
├── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE              # MIT license
└── README.md           # Project overview and documentation
```

---

## 🔄 Core Components

### CLI Layer (`cli.py`)

- Handles command-line arguments using Typer
- Input validation and command routing
- Provides rich terminal output using Rich
- Main entry point via `tidyfiles` command

### Configuration (`config.py`)

- Settings management with three-tier priority:
  1. CLI arguments (highest priority)
  2. User settings file (`~/.tidyfiles/settings.toml`)
  3. Default settings (lowest priority)
- File type mappings and cleaning plans
- Path resolution and validation
- Excludes handling for specific files/directories

### Operations (`operations.py`)

- Core business logic for file organization
- File type detection and categorization
- Directory operations and file moving
- Progress tracking and feedback
- Integration with history tracking

### History Management (`history.py`)

- Operation history tracking and storage
- Session management and status tracking
- Undo functionality for operations and sessions
- History data persistence and retrieval
- Session status management (completed, partially_undone, undone)

### Logging System (`logger.py`)

- Dual logging system:
  - Console output with Rich integration
  - File logging with Loguru (`~/.tidyfiles/tidyfiles.log`)
- Configurable log levels for both outputs
- Error tracking and reporting

---

## 🔀 Data Flow

1. User input → CLI parser (`cli.py`)
2. Settings resolution (`config.py`)
3. Command validation → Operations (`operations.py`)
4. History tracking (`history.py`)
   - Operation recording
   - Session management
   - Undo operations
5. Logging and user feedback (`logger.py`)

---

## 🧪 Testing Strategy

- Unit tests with pytest
- Integration tests for end-to-end workflows
- Minimum 90% code coverage requirement
- Coverage reporting in multiple formats:
  - Terminal output
  - XML report
  - HTML report

---

## 🛠️ Development Tools & Quality Assurance

### Pre-commit Hooks

- Configuration in `.pre-commit-config.yaml`
- Enforces:
  - YAML/TOML validation
  - End of file fixing
  - Trailing whitespace removal
  - Test naming conventions
  - Ruff linting and formatting
  - Commit message validation

### Custom Git Hooks

- Located in `.hooks/` directory
- `commit-msg`: Validates semantic commit messages
- Ensures consistent commit message format across the project

### Continuous Integration

1. **Testing Workflow** (`tests.yml`):
   - Runs on multiple Python versions (3.10-3.13)
   - Executes test suite with pytest
   - Generates coverage reports
   - Uploads results to CodeCov

2. **CodeCov Integration** (`codecov.yml`):
   - Precision: 2 decimal places
   - Project and patch coverage monitoring
   - Ignores test files and setup.py
   - GitHub Checks integration
   - PR comments with coverage details

### Documentation Structure

- **Public Documentation**:
  - Contributing Guidelines
  - Code of Conduct
  - License
  - Main README
- **Internal Documentation**:
  - Release Workflow
  - Development Guidelines
  - Architecture Overview
  - Docs README

---

## 📦 Release Process

- Automated releases via GitHub Actions
- Branch-based release strategy:
  - `main`: Stable releases
  - `rc/*`: Release candidates
  - `beta/*`: Beta releases
  - `alpha/*`: Alpha releases
- Semantic versioning with automated changelog generation
- PyPI publishing with trusted publishing

---

## 🔒 Error Handling

- Comprehensive input validation
- Safe file operations with collision handling
- Detailed error logging
- User-friendly error messages

---

## 🚀 Performance Considerations

- Efficient file type detection
- Progress feedback for large operations
- Memory-efficient file handling
- Proper resource cleanup
