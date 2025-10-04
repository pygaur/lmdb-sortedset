"""
LMDB SortedSet - A Python library providing Redis-like sorted set functionality using LMDB.

This library implements sorted set operations using LMDB (Lightning Memory-Mapped Database)
as the storage backend, providing high-performance, persistent sorted sets with a Redis-compatible API.

Key Features:
- Redis-compatible sorted set operations (zadd, zrange, zrangebyscore, etc.)
- High-performance memory-mapped storage
- ACID transaction support
- Composite key approach for efficient range queries
- JSON serialization support
- Context manager support for automatic cleanup

Example:
    >>> from lmdb_sortedset import LMDBSortedSet
    >>>
    >>> # Create a sorted set client
    >>> with LMDBSortedSet(path="./data") as client:
    >>>     # Add members with scores
    >>>     client.zadd("leaderboard", {"player1": 100, "player2": 200, "player3": 150})
    >>>
    >>>     # Get members by score range
    >>>     players = client.zrangebyscore("leaderboard", 100, 200)
    >>>     print(players)  # ['player1', 'player3', 'player2']
    >>>
    >>>     # Get top players
    >>>     top_players = client.zrange("leaderboard", 0, 2, withscores=True)
    >>>     print(top_players)  # [('player1', 100), ('player3', 150), ('player2', 200)]
"""

from .sortedset import LMDBSortedSet
from .exceptions import LMDBSortedSetError, LMDBInitError, LMDBOperationError

__version__ = "0.1.0"
__author__ = "Prashant"
__all__ = ["LMDBSortedSet", "LMDBSortedSetError", "LMDBInitError", "LMDBOperationError"]
