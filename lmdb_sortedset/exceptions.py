"""
Exception classes for LMDB SortedSet library.
"""


class LMDBSortedSetError(Exception):
    """Base exception for all LMDB SortedSet errors."""

    pass


class LMDBInitError(LMDBSortedSetError):
    """Raised when LMDB initialization fails."""

    pass


class LMDBOperationError(LMDBSortedSetError):
    """Raised when an LMDB operation fails."""

    pass
