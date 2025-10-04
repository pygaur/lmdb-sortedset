#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script to test the LMDB SortedSet library.
"""

import tempfile
import shutil
from pathlib import Path

print("=" * 60)
print("LMDB SortedSet Library - Verification Script")
print("=" * 60)

# Test 1: Import the library
print("\n[1/6] Testing imports...")
try:
    from lmdb_sortedset import LMDBSortedSet, LMDBSortedSetError, LMDBInitError, LMDBOperationError

    print("[PASS] All imports successful")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    exit(1)

# Test 2: Create a temporary database
print("\n[2/6] Creating temporary database...")
temp_dir = tempfile.mkdtemp()
try:
    client = LMDBSortedSet(path=temp_dir)
    print(f"[PASS] Database created at: {temp_dir}")
except Exception as e:
    print(f"[FAIL] Failed to create database: {e}")
    exit(1)

# Test 3: Basic operations
print("\n[3/6] Testing basic operations...")
try:
    # Add members
    result = client.zadd("test", {"member1": 100, "member2": 200, "member3": 150})
    assert result == 3, f"Expected 3, got {result}"

    # Get count
    count = client.zcard("test")
    assert count == 3, f"Expected 3, got {count}"

    # Get range
    members = client.zrange("test", 0, -1)
    assert members == ["member1", "member3", "member2"], f"Unexpected order: {members}"

    # Get with scores
    with_scores = client.zrange("test", 0, -1, withscores=True)
    assert len(with_scores) == 3, f"Expected 3 tuples, got {len(with_scores)}"

    print("[PASS] Basic operations working correctly")
except AssertionError as e:
    print(f"[FAIL] Assertion failed: {e}")
    exit(1)
except Exception as e:
    print(f"[FAIL] Operation failed: {e}")
    exit(1)

# Test 4: Range queries
print("\n[4/6] Testing range queries...")
try:
    # Range by score
    mid_range = client.zrangebyscore("test", 100, 180)
    assert len(mid_range) == 2, f"Expected 2 members, got {len(mid_range)}"

    # Get score
    score = client.zscore("test", "member1")
    assert score == 100.0, f"Expected 100.0, got {score}"

    # Count in range
    count = client.zcount("test", 100, 200)
    assert count == 3, f"Expected 3, got {count}"

    print("[PASS] Range queries working correctly")
except AssertionError as e:
    print(f"[FAIL] Assertion failed: {e}")
    exit(1)
except Exception as e:
    print(f"[FAIL] Operation failed: {e}")
    exit(1)

# Test 5: Removal operations
print("\n[5/6] Testing removal operations...")
try:
    # Remove one member
    removed = client.zrem("test", "member3")
    assert removed == 1, f"Expected 1, got {removed}"

    count = client.zcard("test")
    assert count == 2, f"Expected 2, got {count}"

    # Pop operations
    client.zadd("test", {"member4": 50})
    popped = client.zpopmin("test")
    assert popped[0][0] == "member4", f"Expected member4, got {popped[0][0]}"

    print("[PASS] Removal operations working correctly")
except AssertionError as e:
    print(f"[FAIL] Assertion failed: {e}")
    exit(1)
except Exception as e:
    print(f"[FAIL] Operation failed: {e}")
    exit(1)

# Test 6: Context manager and cleanup
print("\n[6/6] Testing context manager...")
try:
    client.close()

    # Test context manager
    with LMDBSortedSet(path=temp_dir) as ctx_client:
        ctx_client.zadd("ctx_test", {"a": 1})
        count = ctx_client.zcard("ctx_test")
        assert count == 1, f"Expected 1, got {count}"

    print("[PASS] Context manager working correctly")
except Exception as e:
    print(f"[FAIL] Context manager failed: {e}")
    exit(1)
finally:
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

# Summary
print("\n" + "=" * 60)
print("SUCCESS: All tests passed!")
print("=" * 60)
print("\nThe library is ready to use. Try running:")
print("  python examples/basic_usage.py")
print("  pytest tests/")
print("\nFor more information, see README.md")
