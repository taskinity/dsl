# Contributing to DialogChain

Thank you for your interest in contributing to DialogChain! We welcome all contributions, whether they're bug reports, feature requests, documentation improvements, or code contributions.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Before creating a new issue:

1. **Check if the issue has already been reported** by searching under [Issues](https://github.com/dialogchain/python/issues).
2. If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/dialogchain/python/issues/new/choose).

A good bug report includes:

- A clear, descriptive title
- A description of the expected behavior
- A description of the actual behavior
- Steps to reproduce the issue
- Any relevant error messages or logs
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for new features or improvements. Before submitting an enhancement suggestion:

1. Check if the enhancement has already been suggested.
2. Provide a clear and detailed explanation of the suggested enhancement.
3. Include examples of how the enhancement would be used.

### Your First Code Contribution

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/python.git
   cd python
   ```
3. **Set up the development environment** (see [DEVELOPMENT.md](DEVELOPMENT.md)).
4. **Create a branch** for your changes:
   ```bash
   git checkout -b my-feature-branch
   ```
5. **Make your changes** and commit them with a descriptive message.
6. **Push your changes** to your fork.
7. **Create a pull request** to the main repository.

### Pull Requests

Before submitting a pull request:

1. Make sure all tests pass.
2. Ensure your code follows the project's coding standards.
3. Update documentation as needed.
4. Keep pull requests focused and reasonably sized.
5. Reference any related issues in your PR description.

## Development Process

1. **Create a feature branch** from `main`.
2. **Make your changes** and write tests.
3. **Run tests** locally before pushing.
4. **Update documentation** if needed.
5. **Push your branch** and create a pull request.
6. **Address any review comments** and make necessary changes.
7. **Squash commits** if needed for a clean history.
8. **Get your PR approved** and merged.

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
- Use type hints for all function signatures.
- Write docstrings for all public functions and classes.
- Keep functions small and focused on a single responsibility.
- Write unit tests for new functionality.
- Update documentation when adding new features.

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:

```
feat(api): add user authentication endpoint

- Add POST /auth/login endpoint
- Add JWT token generation
- Add authentication middleware

Closes #123
```

## License

By contributing to Taskinity DSL, you agree that your contributions will be licensed under its [MIT License](LICENSE).
