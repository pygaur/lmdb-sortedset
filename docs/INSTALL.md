# Installation Guide

This project can be installed using Poetry (recommended) or traditional pip/setuptools.

## Option 1: Using Poetry (Recommended)

Poetry provides better dependency management and development workflows.

### Step 1: Install Poetry

**macOS/Linux/WSL:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Alternative (using pipx):**
```bash
pipx install poetry
```

Verify installation:
```bash
poetry --version
```

### Step 2: Install the Project

```bash
cd lmdb-sortedset

# Install all dependencies (production + development)
poetry install

# Or install only production dependencies
poetry install --only main
```

### Step 3: Verify Installation

```bash
# Run verification script
poetry run python verify.py

# Or enter the Poetry shell first
poetry shell
python verify.py
```

### Using the Library with Poetry

```bash
# Run Python scripts
poetry run python your_script.py

# Run tests
poetry run pytest

# Or enter the shell
poetry shell
python your_script.py
pytest
exit
```

## Option 2: Using pip (Traditional)

If you prefer not to use Poetry, you can install with pip.

### Install Dependencies

```bash
cd lmdb-sortedset

# Install only lmdb (minimal)
pip install lmdb

# Or install the package in editable mode
pip install -e .

# Install with development dependencies
pip install -e .
pip install -r requirements-dev.txt
```

### Verify Installation

```bash
python3 verify.py
```

### Using the Library with pip

```bash
python your_script.py
pytest
```

## Option 3: Install in Virtual Environment

Using Python's built-in venv:

```bash
cd lmdb-sortedset

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install lmdb
# or
pip install -e .

# Verify
python verify.py

# Deactivate when done
deactivate
```

## Option 4: System-wide Installation

**Not recommended**, but if you need it:

```bash
cd lmdb-sortedset
sudo pip install lmdb
```

## Troubleshooting

### Poetry Not Found After Installation

Add Poetry to your PATH:

```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

### LMDB Installation Issues

If LMDB fails to install:

**macOS:**
```bash
# Install dependencies
brew install lmdb

# Then install Python package
pip install lmdb
```

**Ubuntu/Debian:**
```bash
# Install dependencies
sudo apt-get install liblmdb-dev

# Then install Python package
pip install lmdb
```

**Windows:**
- Ensure you have Visual C++ Build Tools installed
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Permission Errors

If you get permission errors with pip:

```bash
# Use --user flag
pip install --user lmdb

# Or use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install lmdb
```

### Python Version Issues

This project requires Python 3.8 or higher:

```bash
# Check your Python version
python3 --version

# If too old, install newer Python
# macOS:
brew install python@3.11

# Ubuntu/Debian:
sudo apt-get install python3.11
```

## Verification

After installation, verify everything works:

```bash
# Test imports
python3 -c "from lmdb_sortedset import LMDBSortedSet; print('Success!')"

# Run verification script
python3 verify.py

# Run test suite (if dev dependencies installed)
pytest tests/
```

## Quick Reference

### Poetry Commands
```bash
poetry install              # Install dependencies
poetry install --only main  # Production only
poetry add package          # Add dependency
poetry remove package       # Remove dependency
poetry run python script.py # Run script
poetry shell               # Enter venv
poetry build               # Build package
```

### pip Commands
```bash
pip install lmdb           # Install dependency
pip install -e .           # Install package editable
pip install -r requirements-dev.txt  # Install dev deps
python script.py           # Run script
pytest                     # Run tests
```

## Next Steps

After installation:

1. Run verification: `python3 verify.py` or `poetry run python verify.py`
2. Try examples: `python examples/basic_usage.py` or `poetry run python examples/basic_usage.py`
3. Read documentation: See `README.md` and `QUICKSTART.md`
4. Run tests: `pytest` or `poetry run pytest`

## Support

- See `POETRY_GUIDE.md` for detailed Poetry usage
- See `README.md` for API documentation
- See `QUICKSTART.md` for usage examples

