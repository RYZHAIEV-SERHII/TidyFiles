# `Contributing to TidyFiles`

---

First off, thank you for considering contributing to TidyFiles! 🎉

## Quick Links

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Development Guide](docs/internal/DEVELOPMENT.md)
- [Release Workflow](docs/internal/RELEASE_WORKFLOW.md)
- [Project README](README.md)

---

## Ways to Contribute

- Report bugs 🐞
- Suggest features 💡
- Improve documentation 📚
- Submit code changes 🛠️

---

## Development Setup

1. **Fork and clone**:

   ```bash
   git clone https://github.com/YOUR_USERNAME/TidyFiles.git
   cd TidyFiles
   ```

2. **Set up environment**:

   ```bash
   # Install uv if needed
   pip install uv

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate

   # Install dependencies
   uv sync --extras "dev,test"

   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify setup**:

   ```bash
   pytest
   ruff check .
   ```

---

## Development Workflow

1. **Choose the right branch**:
   - `alpha/next`: Experimental features
   - `beta/next`: Stable features needing testing
   - `rc/next`: Release candidate features
   - `main`: Bug fixes and docs

2. **Create your branch**:

   ```bash
   # For features
   git checkout -b feature/name alpha/next

   # For bug fixes
   git checkout -b fix/description main
   ```

3. **Make changes and test**:

   ```bash
   pytest
   ruff check .
   ```

4. **Commit with semantic messages**:

   ```bash
   # Features
   git commit -m "feat: add new feature"

   # Bug fixes
   git commit -m "fix: resolve issue #123"

   # Documentation
   git commit -m "docs: update guide"
   ```

5. **Push and create PR**:

   ```bash
   git push origin your-branch-name
   ```

   Then create PR on GitHub targeting appropriate branch.

---

## Dependency Groups

- **Core**: `uv sync`
- **Dev**: `uv sync --extras dev`
- **Test**: `uv sync --extras test`
- **All**: `uv sync --extras "dev,test"`

---

## Release Process

We follow semantic versioning with staged releases:

```code
main → Stable (0.6.12)
├── rc/next → Release candidates (0.6.12rc1)
├── beta/next → Beta testing (0.6.12b1)
└── alpha/next → Experimental (0.6.12a1)
```

For detailed release procedures, see [Release Workflow](docs/internal/RELEASE_WORKFLOW.md).

---

## Need Help?

- Open an issue for bugs/features
- Start a discussion for questions
- See [README.md](README.md) for more info

---

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---
Thank you for making TidyFiles better! 🚀
