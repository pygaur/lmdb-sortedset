# Poetry Guide for LMDB SortedSet

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

## Why Poetry?

- **Better Dependency Management**: Deterministic builds with `poetry.lock`
- **Virtual Environment Handling**: Automatic venv creation and management
- **Simplified Publishing**: Easy package building and publishing
- **Modern Standards**: Uses pyproject.toml (PEP 518)
- **Development Workflows**: Better separation of dev and prod dependencies

## Installation

### Install Poetry

```bash
# macOS/Linux/WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Alternative: Using pipx
pipx install poetry
```

Verify installation:
```bash
poetry --version
```

## Basic Commands

### Install Project Dependencies

```bash
# Install all dependencies (including dev)
poetry install

# Install only production dependencies
poetry install --only main

# Install without development dependencies
poetry install --no-dev
```

### Add New Dependencies

```bash
# Add a production dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Add with version constraint
poetry add "package-name>=1.0.0,<2.0.0"
```

### Remove Dependencies

```bash
# Remove a dependency
poetry remove package-name

# Remove a dev dependency
poetry remove --group dev package-name
```

### Update Dependencies

```bash
# Update all dependencies
poetry update

# Update specific package
poetry update package-name

# Show outdated packages
poetry show --outdated
```

### Run Commands

```bash
# Run a command in the virtual environment
poetry run python script.py
poetry run pytest
poetry run black .

# Or activate the shell first
poetry shell
python script.py
pytest
```

### Build and Publish

```bash
# Build the package (creates wheel and sdist)
poetry build

# Publish to PyPI
poetry publish

# Publish to Test PyPI
poetry publish --repository testpypi

# Build and publish in one step
poetry publish --build
```

## Project-Specific Commands

### Using Make (Recommended)

We've provided a Makefile for convenience:

```bash
# Install project
make install

# Install with dev dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Run examples
make examples

# Build package
make build

# Clean artifacts
make clean

# Enter shell
make shell
```

### Direct Poetry Commands

```bash
# Install the project
poetry install

# Run tests with coverage
poetry run pytest --cov=lmdb_sortedset --cov-report=html

# Format code with black
poetry run black lmdb_sortedset/ tests/ examples/

# Run linting
poetry run flake8 lmdb_sortedset/
poetry run mypy lmdb_sortedset/

# Run examples
poetry run python examples/basic_usage.py

# Build the package
poetry build
```

## Virtual Environment Management

```bash
# Show virtual environment info
poetry env info

# Show path to virtual environment
poetry env info --path

# List all virtual environments
poetry env list

# Remove virtual environment
poetry env remove python3.11

# Create venv with specific Python version
poetry env use python3.11
poetry env use 3.11
poetry env use /usr/local/bin/python3.11
```

## Dependency Groups

This project uses Poetry's dependency groups:

### Main Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.8"
lmdb = "^1.4.0"
```

### Development Dependencies
```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
```

## Lock File

The `poetry.lock` file ensures reproducible builds:

```bash
# Generate/update lock file
poetry lock

# Install from lock file (default behavior)
poetry install

# Update lock file without installing
poetry lock --no-update
```

## Configuration

### Configure Repositories

```bash
# Add Test PyPI repository
poetry config repositories.testpypi https://test.pypi.org/legacy/

# Configure credentials
poetry config pypi-token.pypi YOUR_PYPI_TOKEN
poetry config pypi-token.testpypi YOUR_TEST_PYPI_TOKEN
```

### Poetry Settings

```bash
# Create venv in project directory
poetry config virtualenvs.in-project true

# Don't create venv (use system Python)
poetry config virtualenvs.create false

# Show configuration
poetry config --list
```

## Troubleshooting

### Virtual Environment Issues

```bash
# Remove and recreate venv
poetry env remove python
poetry install

# Use system Python
poetry config virtualenvs.create false
poetry install
```

### Dependency Conflicts

```bash
# Show dependency tree
poetry show --tree

# Update specific dependency
poetry update package-name

# Clear cache
poetry cache clear pypi --all
```

### Build Issues

```bash
# Clean and rebuild
rm -rf dist/ build/
poetry build
```

## Migration from setup.py

This project was migrated from setup.py to Poetry. The migration included:

1. ✅ Created `pyproject.toml` with Poetry format
2. ✅ Moved dependencies from `requirements.txt` to `pyproject.toml`
3. ✅ Updated `Makefile` to use Poetry commands
4. ✅ Updated documentation (README, QUICKSTART)
5. ✅ Kept minimal `setup.py` for backward compatibility

## Comparison: Poetry vs pip

| Task | pip | Poetry |
|------|-----|--------|
| Install deps | `pip install -e .` | `poetry install` |
| Add dependency | Edit requirements.txt + pip install | `poetry add package` |
| Run tests | `pytest` | `poetry run pytest` |
| Build package | `python setup.py sdist bdist_wheel` | `poetry build` |
| Publish | `twine upload dist/*` | `poetry publish` |
| Lock deps | pip freeze > requirements.txt | `poetry lock` |

## Best Practices

1. **Always commit poetry.lock** - Ensures reproducible builds
2. **Use dependency groups** - Separate dev/prod dependencies
3. **Version constraints** - Use semantic versioning (^1.0.0)
4. **Update regularly** - `poetry update` to get security fixes
5. **Use poetry shell** - For interactive development
6. **Use make commands** - For common tasks

## Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry GitHub](https://github.com/python-poetry/poetry)
- [PEP 518 - pyproject.toml](https://www.python.org/dev/peps/pep-0518/)
- [Poetry Basic Usage](https://python-poetry.org/docs/basic-usage/)
- [Poetry CLI Reference](https://python-poetry.org/docs/cli/)

## Quick Reference

```bash
# One-time setup
poetry install

# Daily workflow
poetry shell              # Enter venv
python script.py          # Run scripts
pytest                    # Run tests
exit                      # Exit venv

# Or use poetry run
poetry run pytest         # Run without entering shell
poetry run python script.py

# Package management
poetry add package        # Add dependency
poetry remove package     # Remove dependency
poetry update            # Update all
poetry show              # List installed

# Build and publish
poetry build             # Build package
poetry publish           # Publish to PyPI
```

---

**Note**: If you prefer traditional pip/setuptools, you can still use `pip install -e .` as the project maintains a minimal `setup.py` for compatibility.

