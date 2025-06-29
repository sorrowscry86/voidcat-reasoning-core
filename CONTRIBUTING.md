# Contributing to VoidCat Reasoning Core

We welcome contributions to VoidCat Reasoning Core! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please treat all contributors with respect and create a welcoming environment for everyone.

## How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide clear descriptions** with steps to reproduce
4. **Include system information** (OS, Python version, etc.)

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Commit with clear messages**: `git commit -m 'Add amazing feature'`
7. **Push to your fork**: `git push origin feature/amazing-feature`
8. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.13+
- Git
- Virtual environment tool (venv, conda, or uv)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/yourusername/voidcat-reasoning-core.git
cd voidcat-reasoning-core

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install in development mode
pip install -e .

# Run tests
python main.py
```

## Coding Standards

### Python Style

- **PEP 8 compliance** for code formatting
- **Type hints** for all function parameters and returns
- **Docstrings** for all classes and functions
- **Descriptive variable names** and clear code structure

### Example Code Style

```python
async def process_query(query: str, model: str = "gpt-4o-mini") -> str:
    """
    Process a user query using the RAG engine.
    
    Args:
        query: The user's question or prompt
        model: OpenAI model to use for reasoning
        
    Returns:
        AI-generated response with RAG context
        
    Raises:
        ValueError: If query is empty or invalid
        APIError: If OpenAI API call fails
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")
    
    # Implementation here...
    return response
```

### Documentation

- **Clear README updates** for new features
- **API documentation** for new endpoints
- **Code comments** for complex logic
- **Examples** for new functionality

## Testing Guidelines

### Test Requirements

- **Test new features** with appropriate test cases
- **Maintain test coverage** for critical functionality
- **Test error conditions** and edge cases
- **Validate API responses** for web endpoints

### Running Tests

```bash
# Run the test harness
python main.py

# Test API endpoints
uvicorn api_gateway:app --reload
# Then test endpoints with curl or Postman
```

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: [team@voidcat-reasoning.com](mailto:team@voidcat-reasoning.com) for private matters

### Resources

- [Project Documentation](README.md)
- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Python Style Guide](https://pep8.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Recognition

Contributors will be recognized in:

- Project README
- Release notes
- Hall of Fame (for significant contributions)

Thank you for contributing to VoidCat Reasoning Core! 🐾
