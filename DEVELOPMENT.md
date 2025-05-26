# Development Guide

This document provides guidelines and instructions for developers working on the Taskinity DSL project.

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management
- Docker and Docker Compose (for running services)
- Node.js (for web components and tooling)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/taskinity-dsl.git
   cd taskinity-dsl
   ```

2. **Set up Python environment**
   ```bash
   # Install Poetry if you haven't already
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install dependencies
   poetry install
   
   # Activate the virtual environment
   poetry shell
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing
```

### Test Coverage

We aim to maintain high test coverage. The minimum required coverage is 80%.

To generate a coverage report:

```bash
coverage run -m pytest
coverage report -m
```

## 🧹 Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **Mypy** for static type checking

Run all code quality checks:

```bash
make check
```

## 📦 Project Structure

```
src/
  taskinity/          # Main package
    __init__.py
    core/             # Core functionality
    api/              # Public API
    connectors/       # Protocol connectors
    utils/            # Utility functions
    config/           # Configuration management

tests/               # Test suites
  unit/              # Unit tests
  integration/       # Integration tests
  e2e/               # End-to-end tests
  fixtures/          # Test fixtures

docs/               # Documentation
  api/               # API documentation
  examples/          # Usage examples

endpoints/           # Protocol endpoint implementations
  grpc/
  http/
  mqtt/
  webrtc/

scripts/             # Utility scripts
```

## 🚀 Development Workflow

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with a descriptive message:
   ```bash
   git commit -m "Add new feature for X"
   ```

3. Run tests and code quality checks:
   ```bash
   make check
   ```

4. Push your changes and create a pull request

## 📝 Code Review Process

1. All changes must be reviewed by at least one other developer
2. Ensure all tests pass before requesting review
3. Update documentation as needed
4. Keep pull requests focused and reasonably sized

## 🐛 Debugging

### VS Code Launch Configuration

Add this to your `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "-v",
                "-s",
                "${workspaceFolder}/tests"
            ],
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

## 🚨 Common Issues

### Dependency Issues

If you encounter dependency conflicts:

```bash
# Remove existing virtual environment
rm -rf $(poetry env info -p)

# Reinstall dependencies
poetry install
```

### Test Failures

If tests are failing:

1. Check if all dependencies are installed
2. Ensure test data is in the correct location
3. Run tests with `-v` for more verbose output

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.
