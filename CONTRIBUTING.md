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

## 🚦 Contributing Workflow

### 1. Fork and Clone
1. Fork the repository on GitHub by clicking the "Fork" button
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/TidyFiles.git
   cd TidyFiles
   ```
3. Add the original repository as upstream:
   ```bash
   git remote add upstream https://github.com/RYZHAIEV-SERHII/TidyFiles.git
   ```

### 2. Branch Selection Guide

Choose the appropriate target branch for your work:

1. **alpha/* branches**:
   - For experimental features
   - Early testing, might have breaking changes
   - Example: `git checkout -b feature/experimental-ai alpha/next`

2. **beta/* branches**:
   - For features that are more stable but need testing
   - Example: `git checkout -b feature/new-gui beta/next`

3. **rc/* branches**:
   - For features ready for release candidate
   - Well-tested changes
   - Example: `git checkout -b feature/final-touches rc/next`

4. **main branch**:
   - For bug fixes
   - Documentation updates
   - Minor improvements
   - Example: `git checkout -b fix/typo main`

### 3. Make Changes
1. Create your feature branch from the appropriate target branch:
   ```bash
   # For experimental feature
   git checkout -b feature/my-experiment alpha/next

   # For stable feature
   git checkout -b feature/my-feature beta/next

   # For release-ready feature
   git checkout -b feature/ready-feature rc/next

   # For bug fix
   git checkout -b fix/bug-description main
   ```

2. Make your changes locally

3. Test your changes:
   ```bash
   pytest
   ruff check .
   ```

4. Keep your branch updated:
   ```bash
   git fetch upstream
   git rebase upstream/your-target-branch
   ```

### 4. Commit
Use semantic commit messages:
```bash
# For new features
git commit -m "feat: add new awesome feature"

# For bug fixes
git commit -m "fix: resolve issue #123"

# For documentation
git commit -m "docs: update installation guide"

# For performance improvements
git commit -m "perf: optimize file sorting"
```

### 5. Push and Create Pull Request
1. Push to your fork:
   ```bash
   git push origin your-branch-name
   ```

2. Create Pull Request:
   - Go to your fork on GitHub
   - Click "Pull Request"
   - Select your branch and the appropriate destination branch:
     - Base repository: `RYZHAIEV-SERHII/TidyFiles`
     - Base branch: (`alpha/*`, `beta/*`, `rc/*`, or `main`)
     - Head repository: `YOUR_USERNAME/TidyFiles`
     - Compare branch: `your-branch-name`
   - Add description:
     - What changes you made
     - Why you made them
     - Any related issues
     - Screenshots if applicable

### 6. Review Process
1. Wait for review from maintainers
2. Make any requested changes:
   ```bash
   # Make changes
   git add .
   git commit -m "fix: address review feedback"
   git push origin your-branch-name
   ```
3. Once approved, your PR will be merged

### 7. After Merge
1. Delete your branch:
   ```bash
   git branch -d your-branch-name
   ```
2. Update your fork:
   ```bash
   git fetch upstream
   git checkout main
   git rebase upstream/main
   git push origin main
   ```

## 🔄 Release Process

When changes are merged into release branches, versions are automatically created:
- `alpha/*` → `0.6.12a1` (Alpha release)
- `beta/*` → `0.6.12b1` (Beta release)
- `rc/*` → `0.6.12rc1` (Release Candidate)
- `main` → `0.6.12` (Stable release)

### Testing Pre-releases
Install different versions:
```bash
# Latest stable
pip install tidyfiles

# Latest pre-release
pip install --pre tidyfiles

# Specific pre-release
pip install tidyfiles==0.6.12rc1  # Release Candidate
pip install tidyfiles==0.6.12b1   # Beta
pip install tidyfiles==0.6.12a1   # Alpha
```

## 🛡️ Code of Conduct
By contributing to TidyFiles, you agree to abide by the Code of Conduct. Be respectful and collaborative to ensure a welcoming environment for everyone!

## 💬 Need Help?
If you have questions or run into issues, feel free to open an issue in the repository or start a discussion. We're here to help!

</br>
Thank you for contributing to TidyFiles! Together, we can make it even better. 🚀
