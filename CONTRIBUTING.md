# Contributing to DialogChain

Thank you for your interest in contributing to DialogChain! We welcome contributions from everyone.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment:
   ```bash
   poetry install
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your changes
2. Make your changes
3. Run tests and linters:
   ```bash
   make test
   make lint
   ```
4. Commit your changes with a descriptive message
5. Push to your fork and submit a pull request

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all new code
- Include docstrings for all public functions and classes
- Keep lines under 88 characters

## Testing

- Write tests for new features and bug fixes
- Run tests with `pytest`
- Maintain at least 80% test coverage

## Reporting Issues

When reporting issues, please include:

- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details

## Pull Requests

- Keep PRs focused and small
- Include tests for new features
- Update documentation as needed
- Reference related issues
