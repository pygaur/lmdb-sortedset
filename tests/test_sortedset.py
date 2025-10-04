"""
Unit tests for LMDB SortedSet library.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from lmdb_sortedset import LMDBSortedSet, LMDBInitError, LMDBOperationError


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sortedset_client(temp_db_path):
    """Create a LMDBSortedSet client for testing."""
    client = LMDBSortedSet(path=temp_db_path)
    yield client
    client.close()


class TestLMDBSortedSetInit:
    """Test initialization and context manager."""

    def test_init_creates_directory(self, temp_db_path):
        """Test that initialization creates the database directory."""
        db_path = Path(temp_db_path) / "subdir"
        client = LMDBSortedSet(path=str(db_path))
        
        assert db_path.exists()
        client.close()

    def test_context_manager(self, temp_db_path):
        """Test context manager support."""
        with LMDBSortedSet(path=temp_db_path) as client:
            client.zadd("test", {"member1": 1.0})
            result = client.zrange("test", 0, -1)
            assert result == ["member1"]

    def test_key_prefix(self, temp_db_path):
        """Test key prefix functionality."""
        with LMDBSortedSet(path=temp_db_path, key_prefix="myapp") as client:
            client.zadd("test", {"member1": 1.0})
            assert client.zcard("test") == 1


class TestZAdd:
    """Test zadd operation."""

    def test_zadd_single_member(self, sortedset_client):
        """Test adding a single member."""
        result = sortedset_client.zadd("test", {"member1": 100})
        assert result == 1

    def test_zadd_multiple_members(self, sortedset_client):
        """Test adding multiple members."""
        result = sortedset_client.zadd("test", {
            "member1": 100,
            "member2": 200,
            "member3": 150
        })
        assert result == 3

    def test_zadd_updates_score(self, sortedset_client):
        """Test that zadd updates existing member's score."""
        sortedset_client.zadd("test", {"member1": 100})
        sortedset_client.zadd("test", {"member1": 200})
        
        score = sortedset_client.zscore("test", "member1")
        assert score == 200.0

    def test_zadd_different_types(self, sortedset_client):
        """Test adding members of different types."""
        result = sortedset_client.zadd("test", {
            "string": 1.0,
            123: 2.0,
            45.67: 3.0
        })
        assert result == 3


class TestZRange:
    """Test zrange operation."""

    def test_zrange_all(self, sortedset_client):
        """Test getting all members."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3})
        result = sortedset_client.zrange("test", 0, -1)
        assert result == ["a", "b", "c"]

    def test_zrange_with_scores(self, sortedset_client):
        """Test getting members with scores."""
        sortedset_client.zadd("test", {"a": 1.0, "b": 2.0, "c": 3.0})
        result = sortedset_client.zrange("test", 0, -1, withscores=True)
        assert result == [("a", 1.0), ("b", 2.0), ("c", 3.0)]

    def test_zrange_slice(self, sortedset_client):
        """Test getting a slice of members."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5})
        result = sortedset_client.zrange("test", 1, 3)
        assert result == ["b", "c", "d"]

    def test_zrange_empty_set(self, sortedset_client):
        """Test zrange on empty set."""
        result = sortedset_client.zrange("nonexistent", 0, -1)
        assert result == []


class TestZRangeByScore:
    """Test zrangebyscore operation."""

    def test_zrangebyscore_basic(self, sortedset_client):
        """Test getting members by score range."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5})
        result = sortedset_client.zrangebyscore("test", 2, 4)
        assert result == ["b", "c", "d"]

    def test_zrangebyscore_with_scores(self, sortedset_client):
        """Test getting members with scores by score range."""
        sortedset_client.zadd("test", {"a": 1.0, "b": 2.0, "c": 3.0})
        result = sortedset_client.zrangebyscore("test", 1.5, 2.5, withscores=True)
        assert result == [("b", 2.0)]

    def test_zrangebyscore_no_matches(self, sortedset_client):
        """Test zrangebyscore with no matching scores."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3})
        result = sortedset_client.zrangebyscore("test", 10, 20)
        assert result == []


class TestZRem:
    """Test zrem operation."""

    def test_zrem_single_member(self, sortedset_client):
        """Test removing a single member."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3})
        result = sortedset_client.zrem("test", "b")
        assert result == 1
        assert sortedset_client.zcard("test") == 2

    def test_zrem_multiple_members(self, sortedset_client):
        """Test removing multiple members."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3, "d": 4})
        result = sortedset_client.zrem("test", "a", "c", "d")
        assert result == 3
        assert sortedset_client.zcard("test") == 1

    def test_zrem_nonexistent_member(self, sortedset_client):
        """Test removing a nonexistent member."""
        sortedset_client.zadd("test", {"a": 1})
        result = sortedset_client.zrem("test", "nonexistent")
        assert result == 0


class TestZCard:
    """Test zcard operation."""

    def test_zcard_basic(self, sortedset_client):
        """Test getting cardinality."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3})
        assert sortedset_client.zcard("test") == 3

    def test_zcard_empty_set(self, sortedset_client):
        """Test cardinality of empty set."""
        assert sortedset_client.zcard("nonexistent") == 0


class TestZScore:
    """Test zscore operation."""

    def test_zscore_existing_member(self, sortedset_client):
        """Test getting score of existing member."""
        sortedset_client.zadd("test", {"player1": 123.45})
        score = sortedset_client.zscore("test", "player1")
        assert score == 123.45

    def test_zscore_nonexistent_member(self, sortedset_client):
        """Test getting score of nonexistent member."""
        sortedset_client.zadd("test", {"a": 1})
        score = sortedset_client.zscore("test", "nonexistent")
        assert score is None


class TestZCount:
    """Test zcount operation."""

    def test_zcount_basic(self, sortedset_client):
        """Test counting members in score range."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5})
        count = sortedset_client.zcount("test", 2, 4)
        assert count == 3

    def test_zcount_no_matches(self, sortedset_client):
        """Test zcount with no matches."""
        sortedset_client.zadd("test", {"a": 1, "b": 2})
        count = sortedset_client.zcount("test", 10, 20)
        assert count == 0


class TestZRemRangeByScore:
    """Test zremrangebyscore operation."""

    def test_zremrangebyscore_basic(self, sortedset_client):
        """Test removing members by score range."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5})
        removed = sortedset_client.zremrangebyscore("test", 2, 4)
        assert removed == 3
        assert sortedset_client.zcard("test") == 2

    def test_zremrangebyscore_no_matches(self, sortedset_client):
        """Test removing with no matches."""
        sortedset_client.zadd("test", {"a": 1, "b": 2})
        removed = sortedset_client.zremrangebyscore("test", 10, 20)
        assert removed == 0


class TestZPopMin:
    """Test zpopmin operation."""

    def test_zpopmin_single(self, sortedset_client):
        """Test popping minimum member."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3})
        result = sortedset_client.zpopmin("test")
        assert result == [("a", 1.0)]
        assert sortedset_client.zcard("test") == 2

    def test_zpopmin_multiple(self, sortedset_client):
        """Test popping multiple minimum members."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3, "d": 4})
        result = sortedset_client.zpopmin("test", count=2)
        assert result == [("a", 1.0), ("b", 2.0)]
        assert sortedset_client.zcard("test") == 2


class TestZPopMax:
    """Test zpopmax operation."""

    def test_zpopmax_single(self, sortedset_client):
        """Test popping maximum member."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3})
        result = sortedset_client.zpopmax("test")
        assert result == [("c", 3.0)]
        assert sortedset_client.zcard("test") == 2

    def test_zpopmax_multiple(self, sortedset_client):
        """Test popping multiple maximum members."""
        sortedset_client.zadd("test", {"a": 1, "b": 2, "c": 3, "d": 4})
        result = sortedset_client.zpopmax("test", count=2)
        assert result == [("d", 4.0), ("c", 3.0)]
        assert sortedset_client.zcard("test") == 2


class TestDelete:
    """Test delete operation."""

    def test_delete_existing_set(self, sortedset_client):
        """Test deleting an existing sorted set."""
        sortedset_client.zadd("test", {"a": 1, "b": 2})
        result = sortedset_client.delete("test")
        assert result is True
        assert sortedset_client.zcard("test") == 0

    def test_delete_nonexistent_set(self, sortedset_client):
        """Test deleting a nonexistent set."""
        result = sortedset_client.delete("nonexistent")
        assert result is False


class TestMultipleSortedSets:
    """Test operations on multiple sorted sets."""

    def test_multiple_sets(self, sortedset_client):
        """Test that multiple sorted sets are independent."""
        sortedset_client.zadd("set1", {"a": 1, "b": 2})
        sortedset_client.zadd("set2", {"x": 10, "y": 20})
        
        assert sortedset_client.zcard("set1") == 2
        assert sortedset_client.zcard("set2") == 2
        
        assert sortedset_client.zrange("set1", 0, -1) == ["a", "b"]
        assert sortedset_client.zrange("set2", 0, -1) == ["x", "y"]


class TestPersistence:
    """Test data persistence across client instances."""

    def test_data_persists(self, temp_db_path):
        """Test that data persists after closing and reopening."""
        # Write data
        with LMDBSortedSet(path=temp_db_path) as client:
            client.zadd("test", {"a": 1, "b": 2, "c": 3})
        
        # Read data in new client
        with LMDBSortedSet(path=temp_db_path) as client:
            result = client.zrange("test", 0, -1)
            assert result == ["a", "b", "c"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


