# Contributing to ApexAI-Core

Thank you for your interest in contributing to ApexAI-Core! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jakelevi88hp/ApexAI-Core.git
   cd ApexAI-Core
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

3. Install development dependencies:
   ```bash
   pip install pytest pytest-cov black flake8 isort
   ```

## Code Style

We follow PEP 8 style guidelines for Python code. Please ensure your code adheres to these standards.

- Use `black` for code formatting:
  ```bash
  black .
  ```

- Use `isort` to sort imports:
  ```bash
  isort .
  ```

- Use `flake8` for linting:
  ```bash
  flake8 .
  ```

## Testing

Write tests for all new features and bug fixes. Run the tests with:

```bash
pytest
```

To generate a coverage report:

```bash
pytest --cov=. --cov-report=html
```

## Pull Request Process

1. Fork the repository and create a new branch from `main`.
2. Make your changes and ensure they pass all tests.
3. Update documentation as needed.
4. Submit a pull request to the `main` branch.
5. Ensure the CI pipeline passes.
6. Wait for review and address any feedback.

## Commit Messages

Follow these guidelines for commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## License

By contributing to ApexAI-Core, you agree that your contributions will be licensed under the project's MIT License.

