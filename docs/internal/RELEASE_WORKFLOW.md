# `Release Workflow Guidelines`

---

## Overview

TidyFiles follows a structured release process using semantic versioning and different release stages (alpha, beta, rc,
stable). This document outlines the workflow for managing releases.

---

## Branch Strategy

```plaintext
main        → Stable releases (0.6.12)
├── rc/next → Release candidates (0.6.12rc1)
├── beta/next → Beta testing (0.6.12b1)
└── alpha/next → Experimental (0.6.12a1)
```

---

## Release Stages

### 1. Alpha Stage

- **Branch**: `alpha/next`
- **Version Format**: `0.6.12a1`
- **Purpose**: Experimental features and early testing
- **Stability**: May contain breaking changes
- **Testing**: Basic functionality tests
- **Audience**: Developers and early adopters

### 2. Beta Stage

- **Branch**: `beta/next`
- **Version Format**: `0.6.12b1`
- **Purpose**: Feature complete, needs real-world testing
- **Stability**: API mostly stable, but may change
- **Testing**: Comprehensive testing suite
- **Audience**: Power users and testers

### 3. Release Candidate (RC)

- **Branch**: `rc/next`
- **Version Format**: `0.6.12rc1`
- **Purpose**: Final testing before stable release
- **Stability**: Feature frozen, only bug fixes
- **Testing**: Full test coverage required
- **Audience**: General users for final validation

### 4. Stable Release

- **Branch**: `main`
- **Version Format**: `0.6.12`
- **Purpose**: Production-ready release
- **Stability**: Stable API and features
- **Testing**: Fully tested and verified
- **Audience**: All users

---

## Release Process

### Automated Release Process

1. Push to appropriate branch triggers GitHub Actions workflow
2. Semantic Release:
    - Analyzes commit messages
    - Determines version bump
    - Updates version in files
    - Creates changelog
    - Creates GitHub release
    - Publishes to PyPI

### Manual Steps for Release Promotion

#### Alpha to Beta

```bash
git checkout beta/next
git merge alpha/next
git push origin beta/next
```

#### Beta to RC

```bash
git checkout rc/next
git merge beta/next
git push origin rc/next
```

#### RC to Stable

```bash
git checkout main
git merge rc/next
git push origin main
```

---

## Version Management

### Semantic Versioning

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

### Commit Convention

```code
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:

- `feat`: New feature (minor)
- `fix`: Bug fix (patch)
- `perf`: Performance improvement (patch)
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

---

## Quality Gates

### Before Alpha Release

- [ ] All tests pass
- [ ] Code compiles without warnings
- [ ] Basic functionality works

### Before Beta Release

- [ ] Feature complete
- [ ] Test coverage >80%
- [ ] Documentation updated
- [ ] No known major bugs

### Before RC Release

- [ ] All tests pass
- [ ] Test coverage >90%
- [ ] Documentation complete
- [ ] Performance tested
- [ ] Security review done

### Before Stable Release

- [ ] All tests pass
- [ ] Test coverage >95%
- [ ] No known bugs
- [ ] All documentation updated
- [ ] Changelog reviewed
- [ ] Release notes prepared

---

## Emergency Hotfix Process

For critical bugs in stable release:

1. Create hotfix branch from `main`

   ```bash
   git checkout -b hotfix/critical-bug main
   ```

2. Fix the bug and commit

   ```bash
   git commit -m "fix: critical bug description"
   ```

3. Merge to main and tag

   ```bash
   git checkout main
   git merge hotfix/critical-bug
   git push origin main
   ```

The automated release process will handle version bump and deployment.

---

## Support Policy

- Latest stable release: Full support
- Previous minor version: Security updates only
- Older versions: No support
- Alpha/Beta/RC: Limited support, may contain bugs

---

## Release Checklist

### Pre-release

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog generated
- [ ] Version numbers updated
- [ ] Dependencies reviewed
- [ ] Security checks passed

### Post-release

- [ ] PyPI package verified
- [ ] Release notes published
- [ ] Documentation deployed
- [ ] Release announced
- [ ] Version tags pushed
