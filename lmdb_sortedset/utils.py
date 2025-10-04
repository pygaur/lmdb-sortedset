"""
Utility functions for encoding/decoding data in LMDB SortedSet.
"""

import json
import struct
from typing import Any, Optional, Union


def encode_value(value: Any) -> Optional[bytes]:
    """
    Encode a value for storage in LMDB.

    Handles different data types:
    - None: Returns None
    - int/float: Converts to string then bytes
    - str: Encodes to UTF-8 bytes
    - dict/list: JSON serializes then encodes
    - bytes: Returns as-is

    Args:
        value: The value to encode

    Returns:
        bytes: The encoded value, or None if input is None

    Example:
        >>> encode_value({"key": "value"})
        b'{"key": "value"}'
    """
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    if isinstance(value, (int, float)):
        return str(value).encode("utf-8")
    if isinstance(value, str):
        return value.encode("utf-8")
    return json.dumps(value).encode("utf-8")


def decode_value(value: Optional[bytes], as_json: bool = False) -> Optional[Union[str, dict, list]]:
    """
    Decode a value from LMDB storage.

    Args:
        value: The bytes value from LMDB
        as_json: Whether to parse the value as JSON

    Returns:
        The decoded value (string, dict, list, etc.)

    Example:
        >>> decode_value(b'{"key": "value"}', as_json=True)
        {'key': 'value'}
    """
    if value is None:
        return None
    if as_json:
        return json.loads(value.decode("utf-8"))
    return value.decode("utf-8")


def encode_score(score: Union[int, float]) -> bytes:
    """
    Encode a numerical score for sorted set storage.

    Uses big-endian double precision format for consistent ordering
    across different platforms and architectures.

    Args:
        score: The score value (int or float)

    Returns:
        bytes: 8-byte big-endian double representation

    Example:
        >>> encode_score(123.45)
        b'@^\\xcc\\xcc\\xcc\\xcc\\xcc\\xcd'
    """
    return struct.pack(">d", float(score))


def decode_score(score_bytes: bytes) -> float:
    """
    Decode a score from its binary representation.

    Args:
        score_bytes: 8-byte big-endian double representation

    Returns:
        float: The decoded score value

    Example:
        >>> decode_score(b'@^\\xcc\\xcc\\xcc\\xcc\\xcc\\xcd')
        123.45
    """
    return struct.unpack(">d", score_bytes)[0]


def format_key(key: Union[str, bytes], prefix: str = "") -> bytes:
    """
    Format a key with an optional prefix for namespace isolation.

    Args:
        key: The key to format (string or bytes)
        prefix: Optional prefix to prepend

    Returns:
        bytes: The formatted key

    Example:
        >>> format_key("mykey", "app")
        b'app:mykey'
    """
    if isinstance(key, bytes):
        key = key.decode("utf-8")

    if prefix:
        return f"{prefix}:{key}".encode("utf-8")
    return key.encode("utf-8")
