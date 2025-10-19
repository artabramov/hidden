"""
Byte-oriented LRU cache keyed by strings. Enforces a global capacity
with an optional per-item cap, promotes entries on access, and evicts
the least-recently used until within budget. Supports insert/update,
fetch with recency bump, removal, and full clear, and exposes live
size and item count properties.
"""

from collections import OrderedDict
from typing import Optional


class LRU:
    """
    LRU cache that stores bytes under string keys.
    Limited both by total size in bytes and optional per-item size.
    """

    def __init__(self, cache_size_bytes: int,
                 item_size_bytes: Optional[int] = None):
        self.cache_size_bytes = cache_size_bytes
        self.item_size_bytes = item_size_bytes
        self.cache: OrderedDict[str, bytes] = OrderedDict()

    @property
    def size(self) -> int:
        """Total size of all cached entries in bytes."""
        return sum(len(v) for v in self.cache.values())

    @property
    def count(self) -> int:
        """Number of cached entries."""
        return len(self.cache)

    def save(self, path: str, value: bytes) -> None:
        """Insert or update a key, enforcing size limits."""
        # Skip oversized values (and remove old if existed)
        if (self.item_size_bytes is not None
                and len(value) > self.item_size_bytes):
            self.cache.pop(path, None)
            return

        if path in self.cache:
            self.cache.move_to_end(path)

        self.cache[path] = value

        # Evict until within total size
        while self.size > self.cache_size_bytes and self.cache:
            self.cache.popitem(last=False)

    def load(self, path: str) -> Optional[bytes]:
        """Return cached value or None if not found."""
        if path not in self.cache:
            return None
        self.cache.move_to_end(path)
        return self.cache[path]

    def delete(self, path: str) -> None:
        """Remove a key if present."""
        self.cache.pop(path, None)

    def clear(self) -> None:
        """Clear cache completely."""
        self.cache.clear()
