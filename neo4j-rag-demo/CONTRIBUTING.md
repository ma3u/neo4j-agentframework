# Contributing to Neo4j RAG System

Thank you for your interest in contributing to the Neo4j RAG System! We welcome contributions from the community and are grateful for your support.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check the [existing issues](https://github.com/yourusername/neo4j-rag-system/issues) to avoid duplicates
2. Create a new issue with a clear title and description
3. Include steps to reproduce (for bugs)
4. Add relevant labels

### Submitting Changes

1. **Fork the Repository**
   ```bash
   # Click "Fork" button on GitHub
   git clone https://github.com/yourusername/neo4j-rag-system.git
   cd neo4j-rag-system
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number
   ```

3. **Make Your Changes**
   - Write clean, readable code
   - Follow existing code style
   - Add docstrings to functions
   - Include type hints where possible

4. **Test Your Changes**
   ```bash
   # Run existing tests
   python test_rag.py
   python test_optimized.py

   # Add new tests if needed
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # or "fix: resolve issue #123"
   # or "docs: update README"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable names
- Maximum line length: 100 characters
- Use Black for formatting:
  ```bash
  pip install black
  black *.py
  ```

### Documentation

- All functions should have docstrings:
  ```python
  def function_name(param1: str, param2: int) -> dict:
      """
      Brief description of the function.

      Args:
          param1: Description of param1
          param2: Description of param2

      Returns:
          Description of return value
      """
  ```

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

## Testing

### Running Tests

```bash
# Unit tests
python test_rag.py

# Performance tests
python test_optimized.py

# Quick validation
python quick_test.py
```

### Adding Tests

When adding new features, please include tests:

```python
def test_new_feature():
    """Test description"""
    # Arrange
    rag = Neo4jRAG()

    # Act
    result = rag.new_feature()

    # Assert
    assert result is not None
    rag.close()
```

## Development Setup

1. **Create Virtual Environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

3. **Start Neo4j**
   ```bash
   docker run -d --name neo4j-rag \
     -p7474:7474 -p7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:5.11
   ```

## Areas for Contribution

### Priority Areas

- 🚀 Performance optimizations
- 📚 Documentation improvements
- 🧪 Test coverage expansion
- 🌐 Multi-language support
- 🔧 Configuration management
- 📊 Visualization tools

### Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`

## Community Guidelines

### Be Respectful

- Use welcoming and inclusive language
- Respect differing viewpoints
- Accept constructive criticism
- Focus on what's best for the community

### Communication

- Join discussions in issues and PRs
- Ask questions if you're unsure
- Provide context for your changes
- Be patient with reviewers

## Review Process

1. All PRs require at least one review
2. CI tests must pass
3. Documentation must be updated if needed
4. Changes should maintain backward compatibility

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Contact maintainers

Thank you for contributing! 🎉