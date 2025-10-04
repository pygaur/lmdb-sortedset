# LMDB SortedSet

A high-performance Python library providing Redis-like sorted set functionality using LMDB (Lightning Memory-Mapped Database) as the storage backend.

## Features

- **Redis-Compatible API**: Familiar Redis sorted set operations (zadd, zrange, zrangebyscore, etc.)
- **High Performance**: Memory-mapped storage for fast read/write operations
- **ACID Transactions**: Built on LMDB's robust transaction support
- **Persistent Storage**: Data persists across restarts
- **Lightweight**: Minimal dependencies (only requires `lmdb`)
- **Type Hints**: Full type hint support for better IDE integration
- **Context Manager**: Automatic resource cleanup with context managers

## Installation

### Prerequisites

This project uses [Poetry](https://python-poetry.org/) for dependency management. Install Poetry first:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Install from source

```bash
cd lmdb-sortedset
poetry install
```

### Install with development dependencies

```bash
poetry install  # Installs all dependencies including dev
```

### Alternative: Install without Poetry

```bash
pip install lmdb>=1.4.0
```

## Quick Start

```python
from lmdb_sortedset import LMDBSortedSet

# Create a sorted set client
with LMDBSortedSet(path="./data") as client:
    # Add members with scores
    client.zadd("leaderboard", {
        "player1": 100,
        "player2": 200,
        "player3": 150
    })
    
    # Get all members in order
    members = client.zrange("leaderboard", 0, -1)
    print(members)  # ['player1', 'player3', 'player2']
    
    # Get members with scores
    members_with_scores = client.zrange("leaderboard", 0, -1, withscores=True)
    print(members_with_scores)  # [('player1', 100.0), ('player3', 150.0), ('player2', 200.0)]
    
    # Get members by score range
    mid_range = client.zrangebyscore("leaderboard", 100, 180)
    print(mid_range)  # ['player1', 'player3']
```

## API Reference

### Initialization

```python
LMDBSortedSet(
    path: str,                  # Directory for LMDB storage
    map_size: int = 10GB,       # Maximum database size
    max_dbs: int = 10,          # Maximum number of named databases
    key_prefix: str = "",       # Optional key prefix for namespacing
    readonly: bool = False,     # Read-only mode
    create: bool = True         # Create database if it doesn't exist
)
```

### Sorted Set Operations

#### `zadd(key, score_dict) -> int`
Add members to a sorted set with scores.

```python
client.zadd("myset", {"member1": 1.0, "member2": 2.0})
```

#### `zrange(key, start, stop, withscores=False) -> list`
Get members by index range.

```python
# Get all members
members = client.zrange("myset", 0, -1)

# Get members with scores
members = client.zrange("myset", 0, -1, withscores=True)
```

#### `zrangebyscore(key, min_score, max_score, withscores=False) -> list`
Get members by score range.

```python
members = client.zrangebyscore("myset", 10, 20)
```

#### `zrem(key, *members) -> int`
Remove members from a sorted set.

```python
count = client.zrem("myset", "member1", "member2")
```

#### `zcard(key) -> int`
Get the number of members in a sorted set.

```python
count = client.zcard("myset")
```

#### `zscore(key, member) -> Optional[float]`
Get the score of a member.

```python
score = client.zscore("myset", "member1")
```

#### `zcount(key, min_score, max_score) -> int`
Count members in a score range.

```python
count = client.zcount("myset", 10, 20)
```

#### `zremrangebyscore(key, min_score, max_score) -> int`
Remove members in a score range.

```python
removed = client.zremrangebyscore("myset", 0, 10)
```

#### `zpopmin(key, count=1) -> list`
Remove and return members with the lowest scores.

```python
members = client.zpopmin("myset", count=2)
```

#### `zpopmax(key, count=1) -> list`
Remove and return members with the highest scores.

```python
members = client.zpopmax("myset", count=2)
```

#### `delete(key) -> bool`
Delete an entire sorted set.

```python
deleted = client.delete("myset")
```

## Use Cases

### 1. Leaderboards

```python
with LMDBSortedSet(path="./data") as client:
    # Add player scores
    client.zadd("game:leaderboard", {
        "player1": 1500,
        "player2": 2300,
        "player3": 1800
    })
    
    # Get top 10 players
    top_players = client.zrange("game:leaderboard", -10, -1, withscores=True)
    top_players.reverse()  # Highest score first
```

### 2. Priority Queues

```python
with LMDBSortedSet(path="./data") as client:
    # Add tasks with priorities (lower score = higher priority)
    client.zadd("tasks", {
        "send_email": 3,
        "fix_bug": 1,
        "update_docs": 5
    })
    
    # Process highest priority task
    task = client.zpopmin("tasks")
```

### 3. Time Series Data

```python
import time

with LMDBSortedSet(path="./data") as client:
    # Store events with timestamps as scores
    client.zadd("user:events", {
        "login": time.time(),
        "purchase": time.time() + 100,
        "logout": time.time() + 200
    })
    
    # Get events in time range
    events = client.zrangebyscore("user:events", start_time, end_time)
```

### 4. Rate Limiting

```python
import time

with LMDBSortedSet(path="./data") as client:
    user_id = "user123"
    current_time = time.time()
    window = 60  # 60 seconds
    
    # Add request timestamp
    client.zadd(f"ratelimit:{user_id}", {str(uuid.uuid4()): current_time})
    
    # Remove old requests outside window
    client.zremrangebyscore(f"ratelimit:{user_id}", 0, current_time - window)
    
    # Check rate limit
    request_count = client.zcard(f"ratelimit:{user_id}")
```

## Running Tests

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=lmdb_sortedset --cov-report=html

# Or use make
make test
```

## Running Examples

```bash
# With Poetry
poetry run python examples/basic_usage.py

# Or use make
make examples

# Or activate the virtual environment first
poetry shell
python examples/basic_usage.py
```

## Performance Characteristics

- **Write Performance**: O(log n) for most operations
- **Read Performance**: O(log n) + O(k) where k is the number of results
- **Space Complexity**: O(n) where n is the number of members
- **Persistence**: All data is immediately persisted to disk (configurable)

## Architecture

LMDB SortedSet uses a composite key approach for efficient sorted set storage:

- **Composite Keys**: Keys are stored as `prefix:key:|:score` where score is a big-endian double
- **Natural Ordering**: LMDB's B+ tree provides natural ordering by score
- **ACID Transactions**: All operations are transactional and thread-safe
- **Memory-Mapped**: Fast access through memory-mapped files

## Comparison with Redis

| Feature | LMDB SortedSet | Redis |
|---------|---------------|-------|
| Persistence | Built-in | Optional |
| Memory Usage | Disk-backed | In-memory |
| Setup | No server needed | Requires server |
| ACID | Full ACID support | Limited |
| Network | Local only | Network support |
| Speed | Very fast for local | Fast over network |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built on top of [LMDB](https://github.com/LMDB/lmdb) - Lightning Memory-Mapped Database
- Inspired by Redis sorted sets API
- Reference implementation from realtime-data-sequencer project

## Requirements

- Python >= 3.8
- lmdb >= 1.4.0

## Support

For issues and questions:
- GitHub Issues: https://github.com/pygaur/lmdb-sortedset/issues
- Documentation: See `docs/` directory for all documentation
- Examples: See `examples/` directory for code examples

## Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Installation Guide](docs/INSTALL.md)** - Detailed installation (Poetry + pip)
- **[Poetry Guide](docs/guides/POETRY_GUIDE.md)** - Poetry development workflow

For a complete overview, see [docs/README.md](docs/README.md)

## Roadmap

- [ ] Support for ZREVRANGE and ZREVRANGEBYSCORE
- [ ] ZUNIONSTORE and ZINTERSTORE operations
- [ ] Async/await support
- [ ] Benchmarking suite
- [ ] Additional serialization options (msgpack, pickle)
- [ ] CLI tool for inspecting sorted sets


