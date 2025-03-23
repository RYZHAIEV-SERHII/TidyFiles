# Contributing to TidyFiles

First off, thank you for considering contributing to TidyFiles! 🎉 Your involvement is highly valued, and we’re excited to have you on board.

## 📝 How to Contribute
Here are some ways you can help improve TidyFiles:
- Report bugs 🐞.
- Suggest new features or enhancements 💡.
- Improve the documentation 📚.
- Submit pull requests with bug fixes, code improvements, or new features 🛠️.

## 💻 Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/TidyFiles.git
   cd TidyFiles
   ```

2. **Set up the development environment**:
   ```bash
   # Install uv if you haven't already
   pip install uv

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install all development dependencies
   uv sync --extras "dev,test"

   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify your setup**:
   ```bash
   # Run tests to ensure everything works
   pytest

   # Run ruff to check code style
   ruff check .
   ```

## 📦 Dependency Management

The project uses different dependency groups:
- **Core**: Essential packages for running the application
- **Dev**: Tools for development, linting, and documentation
- **Test**: Testing frameworks and tools

Common commands:
```bash
# Install only what's needed to run the application
uv sync

# Install development tools (including documentation)
uv sync --extras dev

# Install testing tools
uv sync --extras test

# Install everything for development
uv sync --extras "dev,test"
```

## 🚦 Workflow for Contributing
1. Create a new branch for your work:

```bash
git checkout -b feature-name
```

2. Make and test your changes locally.

3. Commit your changes with a meaningful commit message:

```bash
git commit -m "Add feature-name: brief description"
```

4. Push your changes to your forked repository:

```bash
git push origin feature-name
```

5. Open a Pull Request (PR) to the main repository:

- Go to the original repository on GitHub.

- Click the Pull Requests tab and select New Pull Request.

- Provide a clear description of your changes.

## 🛡️ Code of Conduct
By contributing to TidyFiles, you agree to abide by the Code of Conduct. Be respectful and collaborative to ensure a welcoming environment for everyone!

## 💬 Need Help?
If you have questions or run into issues, feel free to open an issue in the repository or start a discussion. We're here to help!

</br>
Thank you for contributing to TidyFiles! Together, we can make it even better. 🚀
