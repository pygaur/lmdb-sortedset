# Publishing to PyPI

Guide for publishing the LMDB SortedSet library to the Python Package Index ([PyPI](https://pypi.org/)).

## 📋 Pre-Publishing Checklist

Before publishing, ensure:

- [x] Poetry is installed
- [x] Project metadata is complete in `pyproject.toml`
- [x] All tests pass
- [x] Documentation is up to date
- [x] Version number is correct
- [ ] PyPI account created
- [ ] PyPI API token generated

## 🔧 Prerequisites

### 1. Install Poetry

If not already installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Create PyPI Account

1. Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Create an account
3. Verify your email address

### 3. Generate API Token

1. Log in to [https://pypi.org/](https://pypi.org/)
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Give it a name (e.g., "lmdb-sortedset")
5. Scope: "Entire account" (first time) or "Project: lmdb-sortedset" (after first publish)
6. Copy the token (starts with `pypi-`)

**Important**: Save this token securely! You won't be able to see it again.

## 🚀 Publishing Steps

### Step 1: Configure Poetry with PyPI Token

```bash
# Configure PyPI credentials
poetry config pypi-token.pypi YOUR_TOKEN_HERE
```

Or set it as an environment variable:
```bash
export POETRY_PYPI_TOKEN_PYPI=YOUR_TOKEN_HERE
```

### Step 2: Run Tests

Ensure everything works:
```bash
# Run tests
poetry run pytest

# Run verification
poetry run python verify.py

# Check for linting errors
poetry run flake8 lmdb_sortedset/
```

### Step 3: Update Version (if needed)

```bash
# Check current version
poetry version

# Bump version (choose one)
poetry version patch    # 0.1.0 -> 0.1.1
poetry version minor    # 0.1.0 -> 0.2.0
poetry version major    # 0.1.0 -> 1.0.0
```

### Step 4: Build the Package

```bash
# Clean previous builds
rm -rf dist/

# Build both wheel and source distribution
poetry build
```

This creates:
- `dist/lmdb_sortedset-0.1.0-py3-none-any.whl` (wheel)
- `dist/lmdb-sortedset-0.1.0.tar.gz` (source)

### Step 5: Verify the Build

```bash
# Check what's included
tar -tzf dist/lmdb-sortedset-0.1.0.tar.gz

# Install locally to test
pip install dist/lmdb_sortedset-0.1.0-py3-none-any.whl
```

### Step 6: Publish to Test PyPI (Optional but Recommended)

Test the publication process first:

```bash
# Configure Test PyPI repository
poetry config repositories.testpypi https://test.pypi.org/legacy/

# Get a Test PyPI token from https://test.pypi.org/
poetry config pypi-token.testpypi YOUR_TEST_TOKEN_HERE

# Publish to Test PyPI
poetry publish --repository testpypi

# Test installation
pip install --index-url https://test.pypi.org/simple/ lmdb-sortedset
```

### Step 7: Publish to PyPI

Once everything looks good:

```bash
# Publish to PyPI
poetry publish

# Or build and publish in one command
poetry publish --build
```

You'll see output like:
```
Publishing lmdb-sortedset (0.1.0) to PyPI
 - Uploading lmdb_sortedset-0.1.0-py3-none-any.whl 100%
 - Uploading lmdb-sortedset-0.1.0.tar.gz 100%
```

### Step 8: Verify Publication

1. Visit: https://pypi.org/project/lmdb-sortedset/
2. Check the package page
3. Test installation:
   ```bash
   pip install lmdb-sortedset
   ```

## 📦 Using Make Commands

For convenience, use the Makefile:

```bash
# Build the package
make build

# Publish to Test PyPI
make publish-test

# Publish to PyPI
make publish
```

## 🔄 Updating the Package

When you need to publish a new version:

```bash
# 1. Update version
poetry version patch  # or minor/major

# 2. Update CHANGELOG.md with changes

# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to X.Y.Z"

# 4. Create git tag
git tag v0.1.1
git push origin main --tags

# 5. Build and publish
poetry publish --build
```

## 🔐 Security Best Practices

### Using API Tokens (Recommended)

```bash
# Store token in Poetry config (more secure)
poetry config pypi-token.pypi pypi-YOUR-TOKEN

# Or use environment variable
export POETRY_PYPI_TOKEN_PYPI=pypi-YOUR-TOKEN
```

### Using .pypirc (Alternative)

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN
```

**Important**: Never commit tokens to git!

## 📝 Package Metadata

The package metadata is in `pyproject.toml`:

```toml
[tool.poetry]
name = "lmdb-sortedset"
version = "0.1.0"
description = "LMDB-based sorted set implementation with Redis-compatible API"
authors = ["Prashant Gaur <91prashantgaur@gmail.com>"]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/pygaur/lmdb-sortedset"
repository = "https://github.com/pygaur/lmdb-sortedset"
keywords = ["lmdb", "sortedset", "redis", "database", "storage"]
```

## 🐛 Troubleshooting

### "403 Forbidden" Error
- Check your API token is correct
- Ensure token has correct scope
- Verify package name isn't taken

### "400 Bad Request" Error
- Check `pyproject.toml` is valid
- Ensure all required fields are present
- Verify version number format

### Package Name Already Exists
- Choose a different name in `pyproject.toml`
- Or request name transfer if you own it

### Build Fails
```bash
# Clear cache and rebuild
poetry cache clear pypi --all
rm -rf dist/
poetry build
```

## 📊 Post-Publication Checklist

After publishing:

- [ ] Verify package appears on PyPI
- [ ] Test `pip install lmdb-sortedset`
- [ ] Update GitHub README with PyPI badge
- [ ] Create GitHub release with tag
- [ ] Announce on social media/forums
- [ ] Monitor PyPI download statistics

## 🎨 Adding PyPI Badges

Add to your README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/lmdb-sortedset.svg)](https://badge.fury.io/py/lmdb-sortedset)
[![PyPI downloads](https://img.shields.io/pypi/dm/lmdb-sortedset.svg)](https://pypi.org/project/lmdb-sortedset/)
[![Python versions](https://img.shields.io/pypi/pyversions/lmdb-sortedset.svg)](https://pypi.org/project/lmdb-sortedset/)
[![License](https://img.shields.io/pypi/l/lmdb-sortedset.svg)](https://github.com/pygaur/lmdb-sortedset/blob/main/LICENSE)
```

## 📚 Resources

- **PyPI**: https://pypi.org/
- **Test PyPI**: https://test.pypi.org/
- **Poetry Publishing Docs**: https://python-poetry.org/docs/libraries/#publishing-to-pypi
- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/

## 🎯 Quick Reference

```bash
# One-time setup
poetry config pypi-token.pypi YOUR_TOKEN

# Publishing workflow
poetry version patch
poetry build
poetry publish

# Or in one command
poetry publish --build
```

## ⚠️ Important Notes

1. **Package names are permanent** - Choose wisely!
2. **You cannot re-upload the same version** - Must bump version
3. **Deletion is restricted** - Can only be done within 72 hours
4. **Keep tokens secure** - Never commit to git
5. **Test first** - Use Test PyPI before production

---

**Ready to publish?** Follow the steps above and your library will be live on PyPI! 🚀


