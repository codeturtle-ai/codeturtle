# Contributing to FastAPI Security Agent

We welcome contributions to make this project better! Please follow these guidelines to ensure a smooth collaboration.

## How to Contribute

1. **Fork the Repository**: Click the "Fork" button on GitHub and clone your fork locally.
2. **Create a Branch**: Use a descriptive name, e.g., `feature/ai-agent-improvements` or `fix/vulnerability-detection`.
3. **Make Changes**: Implement your feature or fix, ensuring code quality and testing.
4. **Run Tests**: Execute `pytest` to verify your changes don't break existing functionality.
5. **Submit a Pull Request**: Provide a clear description of your changes and reference any related issues.

## Development Setup

- Install dependencies: `pip install -r requirements.txt`
- Set up your `.env` file with necessary API keys.
- Run tests: `pytest`
- Check linting: `black . && isort .`

## Code Standards

- Use type hints for all functions.
- Write docstrings for public methods.
- Follow PEP 8 and use `black` for formatting.
- Ensure security: No hardcoding secrets, validate inputs.
- Add tests for new features.

## Reporting Issues

Open an issue with:
- A clear title and description.
- Steps to reproduce.
- Expected vs. actual behavior.
- Environment details (Python version, OS).

Thank you for contributing!
