# Contributing to ETHYS Python SDK

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the ETHYS x402 Python SDK.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/ethys-python.git
   cd ethys-python
   ```
3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Code Style

We use `ruff` for linting and formatting:

```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Type Checking

We use `mypy` for type checking:

```bash
mypy src
```

### Running Tests

```bash
# Run all tests (mocked, no network required)
pytest

# Run with coverage
pytest --cov=src/ethys402 --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

**Note:** Default tests are mocked and do not require network access. To run live integration tests (optional):

```bash
ETHYS_LIVE_BASE_URL=https://402.ethys.dev pytest tests/
```

### Making Changes

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Run quality checks** before committing:
   ```bash
   ruff check .
   ruff format .
   mypy src
   pytest
   ```

4. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Confirmation that all tests pass

## Pull Request Guidelines

- **Keep PRs focused**: One feature or fix per PR
- **Update tests**: Include tests for new features
- **Update documentation**: Update README or docstrings as needed
- **Follow existing patterns**: Match the code style and structure of existing code
- **All checks must pass**: Linting, type checking, and tests must pass

## Code Review

All PRs require review before merging. Reviewers will check:
- Code quality and style
- Test coverage
- Documentation updates
- Backward compatibility (when applicable)

## Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

## Security Issues

For security vulnerabilities, please email security@ethys.dev instead of opening a public issue.

## Questions?

- Open an issue for questions or discussions
- Check the [ETHYS documentation](https://402.ethys.dev/docs) for protocol details

Thank you for contributing! 🚀

