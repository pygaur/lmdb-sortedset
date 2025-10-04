# Quick Start Guide

## Installation

### Using Poetry (Recommended)

```bash
cd lmdb-sortedset

# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install the project
poetry install
```

### Using pip

```bash
cd lmdb-sortedset
pip install -e .
# Or just install lmdb
pip install lmdb
```

## Basic Usage

### 1. Simple Example

```python
from lmdb_sortedset import LMDBSortedSet

# Create a sorted set
with LMDBSortedSet(path="./my_data") as client:
    # Add some data
    client.zadd("scores", {
        "Alice": 95,
        "Bob": 87,
        "Charlie": 92
    })
    
    # Get all members sorted by score
    members = client.zrange("scores", 0, -1)
    print(members)  # ['Bob', 'Charlie', 'Alice']
```

### 2. Working with Scores

```python
with LMDBSortedSet(path="./my_data") as client:
    client.zadd("scores", {"Alice": 95, "Bob": 87})
    
    # Get members with their scores
    members_with_scores = client.zrange("scores", 0, -1, withscores=True)
    print(members_with_scores)  # [('Bob', 87.0), ('Alice', 95.0)]
    
    # Get a specific member's score
    alice_score = client.zscore("scores", "Alice")
    print(alice_score)  # 95.0
    
    # Count members in a score range
    count = client.zcount("scores", 80, 90)
    print(count)  # 1 (Bob)
```

### 3. Range Queries

```python
with LMDBSortedSet(path="./my_data") as client:
    client.zadd("leaderboard", {
        "player1": 100,
        "player2": 200,
        "player3": 150,
        "player4": 175,
        "player5": 125
    })
    
    # Get members by score range
    mid_range = client.zrangebyscore("leaderboard", 120, 180)
    print(mid_range)  # ['player5', 'player3', 'player4']
    
    # Get top 3 players
    top_3 = client.zrange("leaderboard", -3, -1, withscores=True)
    top_3.reverse()  # Highest first
    for rank, (player, score) in enumerate(top_3, 1):
        print(f"{rank}. {player}: {score}")
```

### 4. Removing Members

```python
with LMDBSortedSet(path="./my_data") as client:
    client.zadd("tasks", {
        "task1": 1,
        "task2": 2,
        "task3": 3,
        "task4": 4,
        "task5": 5
    })
    
    # Remove specific members
    removed = client.zrem("tasks", "task3", "task4")
    print(f"Removed {removed} tasks")
    
    # Remove by score range
    removed = client.zremrangebyscore("tasks", 1, 2)
    print(f"Removed {removed} low priority tasks")
```

### 5. Pop Operations

```python
with LMDBSortedSet(path="./my_data") as client:
    client.zadd("queue", {
        "job1": 1,
        "job2": 2,
        "job3": 3,
        "job4": 4
    })
    
    # Pop lowest score (highest priority)
    job = client.zpopmin("queue")
    print(f"Processing: {job}")  # [('job1', 1.0)]
    
    # Pop multiple highest scores
    jobs = client.zpopmax("queue", count=2)
    print(f"Completed: {jobs}")  # [('job4', 4.0), ('job3', 3.0)]
```

### 6. Multiple Sorted Sets

```python
with LMDBSortedSet(path="./my_data") as client:
    # Create multiple independent sorted sets
    client.zadd("math_scores", {"Alice": 95, "Bob": 87})
    client.zadd("science_scores", {"Alice": 88, "Bob": 91})
    
    # Each set is independent
    print(client.zcard("math_scores"))     # 2
    print(client.zcard("science_scores"))  # 2
    
    # Delete a specific sorted set
    client.delete("math_scores")
    print(client.zcard("math_scores"))     # 0
```

### 7. With Key Prefix (Namespacing)

```python
# Use key prefix for namespace isolation
with LMDBSortedSet(path="./my_data", key_prefix="myapp") as client:
    client.zadd("users", {"user1": 1, "user2": 2})
    # Internally stored as "myapp:users:|:..."
```

## Running Tests

```bash
# Install test dependencies
poetry install

# Run all tests
poetry run pytest

# Run with coverage
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

# Or enter Poetry shell first
poetry shell
python examples/basic_usage.py
```

## Configuration Options

```python
LMDBSortedSet(
    path="./data",              # Storage directory
    map_size=10*1024**3,        # Max DB size (10GB default)
    max_dbs=10,                 # Max number of named DBs
    key_prefix="",              # Optional key prefix
    readonly=False,             # Read-only mode
    create=True                 # Create if not exists
)
```

## Common Patterns

### Leaderboard (Gaming)
```python
# Add player scores
client.zadd("game:leaderboard", {"player1": 1500})

# Get top 10
top_10 = client.zrange("game:leaderboard", -10, -1, withscores=True)
top_10.reverse()
```

### Priority Queue
```python
# Lower score = higher priority
client.zadd("tasks", {"urgent_task": 1, "normal_task": 5})

# Process highest priority
task = client.zpopmin("tasks")
```

### Time Series Events
```python
import time

# Store events with timestamps
client.zadd("events", {"event1": time.time()})

# Get recent events
recent = client.zrangebyscore("events", time.time() - 3600, time.time())
```

### Rate Limiting
```python
import time

# Track requests with timestamps
current_time = time.time()
client.zadd(f"user:{user_id}:requests", {request_id: current_time})

# Clean old requests
client.zremrangebyscore(f"user:{user_id}:requests", 0, current_time - 60)

# Check rate limit
if client.zcard(f"user:{user_id}:requests") > 100:
    print("Rate limit exceeded!")
```

## Performance Tips

1. **Use Context Managers**: Always use `with` statement for automatic cleanup
2. **Batch Operations**: Use single `zadd` call for multiple members
3. **Key Prefixing**: Use key prefixes for logical namespacing
4. **Map Size**: Set appropriate `map_size` based on your data volume
5. **Read-Only Mode**: Use `readonly=True` for read-only workloads

## Troubleshooting

### Permission Errors
```bash
mkdir -p ./data
chmod 755 ./data
```

### Database Size Issues
Increase `map_size` when creating the client:
```python
LMDBSortedSet(path="./data", map_size=100*1024**3)  # 100GB
```

### Import Errors
```bash
pip install lmdb
```

## Next Steps

- Read the full [README.md](README.md) for complete API documentation
- Check out [examples/basic_usage.py](examples/basic_usage.py) for more examples
- Run the test suite to verify installation: `pytest tests/`

## Support

For issues and questions, please check:
- [GitHub Issues](https://github.com/yourusername/lmdb-sortedset/issues)
- Examples in the `examples/` directory
- Test cases in the `tests/` directory


