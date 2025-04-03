# `Development Guidelines`

---

## 🛠️ Development Environment

### Prerequisites

- Python 3.10 or higher
- `uv` package manager
- Git

### Initial Setup

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/TidyFiles.git
cd TidyFiles

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync --extras "dev,test"

# Install pre-commit hooks
pre-commit install
```

---

## 🔍 Code Quality Standards

### Code Style

- We use `ruff` for linting and formatting
- Maximum line length: 88 characters
- Use type hints for all function parameters and return values
- Document all public functions and classes

### Testing

- All new features must include tests
- Maintain minimum 95% code coverage (as specified in Release Workflow)
- Run tests locally before pushing:

  ```bash
  pytest
  ```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
# Run manually
pre-commit run --all-files
```

---

## 🐛 Debugging Tips

- Use `--log-console-level DEBUG` for detailed logging
- Common debugging scenarios:
  - File organization issues: Check permissions and paths
  - Configuration problems: Verify YAML syntax
  - Plugin failures: Check plugin compatibility
- Using debugger with CLI:

  ```python
  import debugpy
  debugpy.listen(5678)
  debugpy.wait_for_client()  # Add this line where you want to break
  ```

---

## 📦 Building and Testing Locally

```bash
# Build package
uv build

# Install locally
pip install dist/tidyfiles-*.whl

# Test the installed package
tidyfiles --version
```

---

## 🔄 Common Development Tasks

### Adding New File Types

1. Update `tidyfiles/constants.py`:

   ```python
   FILE_TYPES = {
       "new_type": [".ext1", ".ext2"]
   }
   ```

2. Add corresponding tests in `tests/test_file_types.py`
3. Update documentation in `README.md`

### Adding New Commands

1. Add command in `tidyfiles/cli.py`:

   ```python
   @app.command()
   def new_command():
       """Command description."""
       pass
   ```

2. Create handler in appropriate module
3. Add tests and documentation

### Performance Optimization

- Use profiling tools:

  ```bash
  python -m cProfile -o profile.stats your_script.py
  ```

- Monitor memory usage
- Implement batch processing for large directories

---

## 📚 Documentation Standards

- Use Google-style docstrings
- Keep README.md up to date
- Document breaking changes
- Include examples for new features

---

## 🔒 Security Guidelines

- Validate all file operations
- Handle permissions carefully
- Never store sensitive data
- Use secure default settings

---

## 🤝 Code Review Process

1. Self-review checklist
2. Request review from maintainers
3. Address feedback promptly
4. Update tests if needed

---

## 📈 Performance Considerations

- Batch operations when possible
- Use generators for large datasets
- Cache frequent operations
- Profile critical paths

For more information about releases and versioning, see [Release Workflow](RELEASE_WORKFLOW.md).
