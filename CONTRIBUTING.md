# Contributing to Real-Time Agent

We welcome contributions to the Real-Time Agent project! This document provides guidelines for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/real-time-agent.git
   cd real-time-agent
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines
3. Add tests for new functionality
4. Run tests to ensure everything works
5. Update documentation as needed

## Code Style

- Follow PEP 8 for Python code style
- Use type hints for all function parameters and return values
- Add docstrings for all public functions and classes
- Keep line length to 100 characters maximum

## Testing

Run tests before submitting:

```bash
# Run basic tests
python tests/test_basic.py

# With pytest (if available)
pytest tests/
```

## Submitting Changes

1. Commit your changes with descriptive messages
2. Push to your fork
3. Create a pull request with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots for UI changes

## Issues

When reporting issues, please include:
- Python version
- Operating system
- Error messages and stack traces
- Steps to reproduce
- Expected vs actual behavior

Thank you for contributing!
