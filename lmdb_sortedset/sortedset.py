"""
LMDB-based sorted set implementation with Redis-compatible API.

This module provides a high-performance sorted set implementation using LMDB
as the storage backend. It implements Redis-like sorted set operations with
persistent storage and ACID transaction support.
"""

import lmdb
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from .utils import encode_value, decode_value, encode_score, decode_score, format_key
from .exceptions import LMDBInitError, LMDBOperationError


logger = logging.getLogger(__name__)


class LMDBSortedSet:
    """
    LMDB-based sorted set implementation with Redis-compatible API.

    This class provides high-performance sorted set operations using LMDB as the
    storage backend. It uses a composite key approach for efficient range queries
    and maintains compatibility with Redis sorted set operations.

    Key Design Decisions:
    1. Composite Keys: Sorted sets use keys in format 'prefix:key:score' for natural ordering
    2. Binary Score Encoding: Scores are stored as big-endian doubles for consistent ordering
    3. ACID Transactions: All operations are transactional
    4. Context Manager: Supports automatic resource cleanup

    Attributes:
        env: LMDB environment instance
        zset_db: Database for sorted sets
        SCORE_SEPARATOR: Byte separator for composite keys

    Example:
        >>> with LMDBSortedSet(path="./data") as client:
        >>>     client.zadd("myset", {"member1": 1.0, "member2": 2.0})
        >>>     members = client.zrange("myset", 0, -1)
        >>>     print(members)  # ['member1', 'member2']
    """

    # Special token to separate score from value in sorted sets
    SCORE_SEPARATOR = b":|:"

    def __init__(
        self,
        path: str,
        map_size: int = 10 * 1024 * 1024 * 1024,  # 10GB default
        max_dbs: int = 10,
        key_prefix: str = "",
        readonly: bool = False,
        create: bool = True,
    ):
        """
        Initialize the LMDB sorted set client.

        Args:
            path: Directory path for LMDB storage
            map_size: Maximum size of the database (default: 10GB)
            max_dbs: Maximum number of named databases (default: 10)
            key_prefix: Optional prefix for all keys for namespace isolation
            readonly: Whether to open the database in read-only mode
            create: Whether to create the database if it doesn't exist

        Raises:
            LMDBInitError: If LMDB initialization fails
        """
        self.path = path
        self.key_prefix = key_prefix
        self.env = None
        self.zset_db = None

        try:
            # Ensure directory exists with proper permissions
            path_obj = Path(path)
            if create and not readonly:
                path_obj.mkdir(parents=True, exist_ok=True)

            # Initialize the LMDB environment
            self.env = lmdb.open(
                path,
                map_size=map_size,
                max_dbs=max_dbs,
                subdir=True,
                metasync=True,
                sync=True,
                map_async=False,
                mode=0o755,
                readonly=readonly,
                create=create,
            )

            # Create database for sorted sets
            self.zset_db = self.env.open_db(b"zset")

            logger.info(f"LMDB SortedSet initialized at: {path}")

        except lmdb.Error as e:
            error_msg = f"LMDB initialization error: {e}. Path: {path}"
            logger.error(error_msg)
            if not readonly:
                logger.error(
                    f"Verify that the directory exists and has correct permissions "
                    f"(try: mkdir -p {path} && chmod 755 {path})"
                )
            raise LMDBInitError(error_msg) from e

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()

    def _format_key(self, key: Union[str, bytes]) -> bytes:
        """
        Format a key with the global prefix for namespace isolation.

        Args:
            key: The key to format (string or bytes)

        Returns:
            bytes: The formatted key with prefix
        """
        return format_key(key, self.key_prefix)

    def _zset_key(self, key: Union[str, bytes], score: Union[int, float]) -> bytes:
        """
        Create a composite key for sorted set that ensures ordering by score.

        The composite key format is: 'prefix:key:|:score' where score is encoded
        as a big-endian double. This ensures natural ordering by score when
        iterating through keys.

        Args:
            key: The sorted set key
            score: The score value

        Returns:
            bytes: The composite key
        """
        formatted_key = self._format_key(key)
        score_bytes = encode_score(score)
        return formatted_key + self.SCORE_SEPARATOR + score_bytes

    def _extract_from_zset_key(self, compound_key: bytes) -> Tuple[bytes, float]:
        """
        Extract original key and score from compound key.

        Args:
            compound_key: The composite key from sorted set

        Returns:
            tuple: (original_key, score)
        """
        key_part, score_part = compound_key.split(self.SCORE_SEPARATOR, 1)
        score = decode_score(score_part)
        return key_part, score

    def zadd(self, key: Union[str, bytes], score_dict: Dict[Any, Union[int, float]]) -> int:
        """
        Add one or more members to a sorted set, or update their scores.

        Args:
            key: The sorted set key
            score_dict: Dictionary mapping members to scores

        Returns:
            int: Number of members added/updated

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zadd("leaderboard", {"player1": 100, "player2": 200})
            2
        """
        try:
            result = 0
            zset_key = self._format_key(key)

            with self.env.begin(db=self.zset_db, write=True) as txn:
                for member, score in score_dict.items():
                    # Create composite key that ensures ordering by score
                    compound_key = self._zset_key(key, score)
                    encoded_value = encode_value(member)
                    txn.put(compound_key, encoded_value)
                    result += 1

            return result

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to add members to sorted set: {e}") from e

    def zrange(
        self,
        key: Union[str, bytes],
        start: int,
        stop: int,
        withscores: bool = False,
    ) -> Union[List[Any], List[Tuple[Any, float]]]:
        """
        Get a range of elements from a sorted set by index.

        Args:
            key: The sorted set key
            start: Start index (0-based)
            stop: Stop index (inclusive, -1 for end)
            withscores: Whether to include scores in results

        Returns:
            list: List of members or (member, score) tuples if withscores=True

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zrange("leaderboard", 0, -1, withscores=True)
            [('player1', 100.0), ('player2', 200.0)]
        """
        try:
            results = []
            zset_key = self._format_key(key)

            with self.env.begin(db=self.zset_db, write=False) as txn:
                cursor = txn.cursor()
                if cursor.set_range(zset_key):
                    # First, check if we have any data
                    compound_key = cursor.key()
                    if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                        return results

                    # Collect all items first to handle negative indices
                    all_items = []
                    for compound_key, value in cursor.iternext():
                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break
                        _, score = self._extract_from_zset_key(compound_key)
                        all_items.append((decode_value(value), score))

                    # Handle negative indices
                    if stop == -1:
                        stop = len(all_items) - 1
                    if start < 0:
                        start = max(0, len(all_items) + start)
                    if stop < 0:
                        stop = max(0, len(all_items) + stop)

                    # Slice the results
                    for item in all_items[start : stop + 1]:
                        if withscores:
                            results.append(item)
                        else:
                            results.append(item[0])

            return results

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to get range from sorted set: {e}") from e

    def zrangebyscore(
        self,
        key: Union[str, bytes],
        min_score: Union[int, float],
        max_score: Union[int, float],
        withscores: bool = False,
    ) -> Union[List[Any], List[Tuple[Any, float]]]:
        """
        Get members in a sorted set with scores within the given range.

        Args:
            key: The sorted set key
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)
            withscores: Whether to include scores in results

        Returns:
            list: List of members or (member, score) tuples if withscores=True

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zrangebyscore("leaderboard", 100, 200)
            ['player1', 'player2']
        """
        try:
            results = []
            zset_key = self._format_key(key)
            min_compound = self._zset_key(key, min_score)

            with self.env.begin(db=self.zset_db, write=False) as txn:
                cursor = txn.cursor()
                if cursor.set_range(min_compound):
                    for compound_key, value in cursor:
                        # Check if we're still in the same sorted set
                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break

                        # Extract the score and check if it's within range
                        _, score = self._extract_from_zset_key(compound_key)
                        if score > max_score:
                            break

                        if withscores:
                            results.append((decode_value(value), score))
                        else:
                            results.append(decode_value(value))

            return results

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to get range by score: {e}") from e

    def zrem(self, key: Union[str, bytes], *members: Any) -> int:
        """
        Remove one or more members from a sorted set.

        Args:
            key: The sorted set key
            *members: One or more members to remove

        Returns:
            int: Number of members removed

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zrem("leaderboard", "player1", "player2")
            2
        """
        try:
            zset_key = self._format_key(key)
            removed = 0

            with self.env.begin(db=self.zset_db, write=True) as txn:
                for member in members:
                    encoded_value = encode_value(member)
                    cursor = txn.cursor()
                    
                    if cursor.set_range(zset_key):
                        for compound_key, stored_value in cursor:
                            # Check if we're still in the same sorted set
                            if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                                break

                            if stored_value == encoded_value:
                                cursor.delete()
                                removed += 1
                                break

            return removed

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to remove members from sorted set: {e}") from e

    def zcard(self, key: Union[str, bytes]) -> int:
        """
        Get the number of members in a sorted set.

        Args:
            key: The sorted set key

        Returns:
            int: Number of members

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zcard("leaderboard")
            5
        """
        try:
            count = 0
            zset_key = self._format_key(key)

            with self.env.begin(db=self.zset_db, write=False) as txn:
                cursor = txn.cursor()
                if cursor.set_range(zset_key):
                    for compound_key, _ in cursor:
                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break
                        count += 1

            return count

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to get cardinality: {e}") from e

    def zscore(self, key: Union[str, bytes], member: Any) -> Optional[float]:
        """
        Get the score of a member in a sorted set.

        Args:
            key: The sorted set key
            member: The member to get the score for

        Returns:
            float: The score, or None if member doesn't exist

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zscore("leaderboard", "player1")
            100.0
        """
        try:
            zset_key = self._format_key(key)
            encoded_value = encode_value(member)

            with self.env.begin(db=self.zset_db, write=False) as txn:
                cursor = txn.cursor()
                if cursor.set_range(zset_key):
                    for compound_key, stored_value in cursor:
                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break

                        if stored_value == encoded_value:
                            _, score = self._extract_from_zset_key(compound_key)
                            return score

            return None

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to get score: {e}") from e

    def zcount(
        self,
        key: Union[str, bytes],
        min_score: Union[int, float],
        max_score: Union[int, float],
    ) -> int:
        """
        Count members in a sorted set with scores within the given range.

        Args:
            key: The sorted set key
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)

        Returns:
            int: Number of members in the score range

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zcount("leaderboard", 100, 200)
            3
        """
        try:
            count = 0
            zset_key = self._format_key(key)
            min_compound = self._zset_key(key, min_score)

            with self.env.begin(db=self.zset_db, write=False) as txn:
                cursor = txn.cursor()
                if cursor.set_range(min_compound):
                    for compound_key, _ in cursor:
                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break

                        _, score = self._extract_from_zset_key(compound_key)
                        if score > max_score:
                            break

                        count += 1

            return count

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to count members: {e}") from e

    def zremrangebyscore(
        self,
        key: Union[str, bytes],
        min_score: Union[int, float],
        max_score: Union[int, float],
    ) -> int:
        """
        Remove all members in a sorted set with scores within the given range.

        Args:
            key: The sorted set key
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)

        Returns:
            int: Number of members removed

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zremrangebyscore("leaderboard", 0, 100)
            2
        """
        try:
            removed = 0
            zset_key = self._format_key(key)
            min_compound = self._zset_key(key, min_score)

            with self.env.begin(db=self.zset_db, write=True) as txn:
                cursor = txn.cursor()
                if cursor.set_range(min_compound):
                    for compound_key, _ in list(cursor.iternext()):
                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break

                        _, score = self._extract_from_zset_key(compound_key)
                        if score > max_score:
                            break

                        cursor.delete()
                        removed += 1

            return removed

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to remove range by score: {e}") from e

    def zpopmin(self, key: Union[str, bytes], count: int = 1) -> List[Tuple[Any, float]]:
        """
        Remove and return up to count members with the lowest scores.

        Args:
            key: The sorted set key
            count: Number of members to pop (default: 1)

        Returns:
            list: List of (member, score) tuples

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zpopmin("leaderboard", 2)
            [('player3', 50.0), ('player1', 100.0)]
        """
        try:
            results = []
            zset_key = self._format_key(key)

            with self.env.begin(db=self.zset_db, write=True) as txn:
                cursor = txn.cursor()
                if cursor.set_range(zset_key):
                    popped = 0
                    for compound_key, value in list(cursor.iternext()):
                        if popped >= count:
                            break

                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break

                        _, score = self._extract_from_zset_key(compound_key)
                        results.append((decode_value(value), score))
                        cursor.delete()
                        popped += 1

            return results

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to pop min: {e}") from e

    def zpopmax(self, key: Union[str, bytes], count: int = 1) -> List[Tuple[Any, float]]:
        """
        Remove and return up to count members with the highest scores.

        Args:
            key: The sorted set key
            count: Number of members to pop (default: 1)

        Returns:
            list: List of (member, score) tuples in descending order

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.zpopmax("leaderboard", 2)
            [('player2', 200.0), ('player1', 100.0)]
        """
        try:
            # Get all items, then remove from the end
            items = self.zrange(key, 0, -1, withscores=True)
            
            if not items:
                return []

            # Take the last 'count' items
            to_remove = items[-count:] if count < len(items) else items
            to_remove.reverse()  # Highest score first

            # Remove them
            members = [item[0] for item in to_remove]
            self.zrem(key, *members)

            return to_remove

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to pop max: {e}") from e

    def delete(self, key: Union[str, bytes]) -> bool:
        """
        Delete an entire sorted set.

        Args:
            key: The sorted set key

        Returns:
            bool: True if the set was deleted, False if it didn't exist

        Raises:
            LMDBOperationError: If the operation fails

        Example:
            >>> client.delete("leaderboard")
            True
        """
        try:
            zset_key = self._format_key(key)
            deleted = False

            with self.env.begin(db=self.zset_db, write=True) as txn:
                cursor = txn.cursor()
                if cursor.set_range(zset_key):
                    for compound_key, _ in list(cursor.iternext()):
                        if not compound_key.startswith(zset_key + self.SCORE_SEPARATOR):
                            break
                        cursor.delete()
                        deleted = True

            return deleted

        except lmdb.Error as e:
            raise LMDBOperationError(f"Failed to delete sorted set: {e}") from e

    def close(self):
        """
        Close the LMDB environment and release resources.

        This method should be called when the client is no longer needed
        to ensure proper cleanup of LMDB resources.
        """
        if self.env:
            self.env.close()
            logger.info(f"LMDB SortedSet closed: {self.path}")


