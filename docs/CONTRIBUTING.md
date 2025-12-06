# Contributing to Maestrai

Thank you for your interest in contributing to Maestrai! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Prioritize community well-being

### Our Responsibilities

Project maintainers will:
- Clearly communicate expectations
- Address unacceptable behavior
- Make fair and consistent decisions

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- FFmpeg
- Basic understanding of audio processing and machine learning

### Find an Issue

1. Check [existing issues](https://github.com/yourusername/maestrai/issues)
2. Look for labels like `good first issue` or `help wanted`
3. Comment on the issue to express interest
4. Wait for maintainer confirmation before starting

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/maestrai.git
cd maestrai

# Add upstream remote
git remote add upstream https://github.com/yourusername/maestrai.git
```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

### 4. Verify Setup

```bash
# Run tests
pytest tests/

# Check code style
black --check src/ tests/
flake8 src/ tests/
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions/changes
- `refactor/` - Code refactoring

### 2. Make Your Changes

- Follow existing code style
- Add type hints
- Write docstrings (Google style)
- Add tests for new features
- Update documentation

### 3. Write Good Commit Messages

```
<type>: <short summary>

<detailed description>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

Example:
```
feat: Add support for OPUS audio format

- Add .opus to supported audio formats
- Update AudioProcessor validation
- Add tests for OPUS files
- Update documentation

Closes #123
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_transcription.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_transcription.py::TestAudioProcessor::test_validate_nonexistent_file
```

### Writing Tests

1. Add tests in `tests/` directory
2. Use descriptive test names
3. Follow existing test patterns
4. Aim for good coverage

Example:
```python
def test_new_feature(self):
    """Test that new feature works correctly."""
    # Arrange
    input_data = "test"

    # Act
    result = function_to_test(input_data)

    # Assert
    self.assertEqual(result, expected_output)
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- Line length: 100 characters
- Use Black for formatting
- Use type hints
- Write docstrings for all public functions

### Type Hints

```python
def transcribe(
    audio_path: str | Path,
    language: Optional[str] = None
) -> TranscriptionResult:
    """Transcribe an audio file."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
    """
    pass
```

### Formatting Tools

```bash
# Format code with Black
black src/ tests/

# Check with flake8
flake8 src/ tests/

# Type check with mypy
mypy src/
```

## Pull Request Process

### 1. Update Your Branch

```bash
# Fetch upstream changes
git fetch upstream

# Merge or rebase
git rebase upstream/main
```

### 2. Push Your Changes

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill out the PR template
3. Link related issues
4. Request review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Closes #123
```

### 4. Code Review

- Respond to feedback promptly
- Make requested changes
- Push updates to the same branch
- Mark conversations as resolved

### 5. Merge

Once approved:
- Maintainer will merge your PR
- Delete your branch after merge

## Reporting Issues

### Bug Reports

Use the bug report template:

```markdown
## Description
Clear description of the bug

## To Reproduce
Steps to reproduce:
1. Run command '...'
2. Use file '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 13.0]
- Python: [e.g., 3.10.5]
- Maestrai version: [e.g., 1.0.0]

## Additional Context
Logs, screenshots, etc.
```

### Feature Requests

Use the feature request template:

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches considered

## Additional Context
Any other relevant info
```

## Development Guidelines

### Adding New Features

1. **Plan First**
   - Discuss in an issue
   - Get feedback on approach
   - Consider impact on existing code

2. **Implement**
   - Write clean, modular code
   - Follow existing patterns
   - Add comprehensive tests

3. **Document**
   - Update README if needed
   - Add API documentation
   - Include examples

### Modifying Core Components

Changes to core components require:
- Detailed explanation
- Backwards compatibility consideration
- Comprehensive testing
- Documentation updates

### Adding Dependencies

- Justify the need
- Consider impact on users
- Update requirements files
- Document usage

## Release Process

(For maintainers)

1. Update version in `setup.py` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch
4. Test thoroughly
5. Merge to main
6. Tag release
7. Publish to PyPI
8. Create GitHub release

## Community

### Communication

- GitHub Issues: Bug reports and feature requests
- Pull Requests: Code contributions
- Discussions: General questions and ideas

### Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- README acknowledgments

## Questions?

- Check existing documentation
- Search closed issues
- Open a discussion
- Ask maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Maestrai! 🎉
