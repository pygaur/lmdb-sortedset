# LMDB SortedSet Documentation

High-performance sorted set implementation using LMDB with Redis-compatible API.

## 🚀 Quick Start

### Installation

**Using Poetry** (recommended):
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry install
```

**Using pip**:
```bash
pip install lmdb
```

### Basic Usage

```python
from lmdb_sortedset import LMDBSortedSet

# Create a sorted set
with LMDBSortedSet(path="./data") as client:
    # Add members with scores
    client.zadd("leaderboard", {
        "player1": 100,
        "player2": 200,
        "player3": 150
    })
    
    # Get all members sorted by score
    members = client.zrange("leaderboard", 0, -1)
    print(members)  # ['player1', 'player3', 'player2']
```

See [QUICKSTART.md](QUICKSTART.md) for detailed examples.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide with examples |
| [INSTALL.md](INSTALL.md) | Installation instructions (Poetry + pip) |
| [guides/POETRY_GUIDE.md](guides/POETRY_GUIDE.md) | Complete Poetry usage guide |
| [../README.md](../README.md) | Complete API reference |

## 🎓 Learn More

### Getting Started
1. **New to the library?** → Start with [QUICKSTART.md](QUICKSTART.md)
2. **Installing?** → See [INSTALL.md](INSTALL.md)
3. **Using Poetry?** → Check [guides/POETRY_GUIDE.md](guides/POETRY_GUIDE.md)

### API Reference
See the main [README.md](../README.md) for complete API documentation.

### Examples
Check the `examples/` directory for working code:
- `examples/basic_usage.py` - 6 real-world use cases

## 🛠️ Development

### Using Poetry

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run examples
poetry run python examples/basic_usage.py

# Format code
poetry run black lmdb_sortedset/
```

### Using Make

```bash
make install-dev  # Install with dev dependencies
make test         # Run tests
make examples     # Run examples
```

## 📦 Project Info

- **Name**: lmdb-sortedset
- **Version**: 0.1.0
- **License**: MIT
- **Author**: Prashant Gaur <91prashantgaur@gmail.com>
- **Repository**: https://github.com/pygaur/lmdb-sortedset

## 🤝 Contributing

1. Install Poetry and dependencies: `poetry install`
2. Run tests: `poetry run pytest`
3. Follow code style: `poetry run black lmdb_sortedset/`

See [guides/POETRY_GUIDE.md](guides/POETRY_GUIDE.md) for development workflow.

## 📞 Support

- **GitHub Issues**: https://github.com/pygaur/lmdb-sortedset/issues
- **Documentation**: You're reading it!
- **Examples**: See `examples/` directory

## 🔗 Links

- [PyPI Package](https://pypi.org/project/lmdb-sortedset/) (coming soon)
- [GitHub Repository](https://github.com/pygaur/lmdb-sortedset)
- [Poetry Documentation](https://python-poetry.org/docs/)

---

**Ready to use?** Check [QUICKSTART.md](QUICKSTART.md) to get started in 5 minutes!
