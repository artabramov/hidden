# app/cache/lru.py
# SPDX-License-Identifier: SSPL-1.0

from collections import OrderedDict
from functools import lru_cache

from app.config import get_config

# NOTE (ADR-58): LRU cache holds decrypted bytes in process memory.
# This avoids repeated gocryptfs reads for frequently requested
# thumbnails. Plaintext may temporarily reach swap; sensitive
# deployments should disable swap or use encrypted swap. The cache
# is process-local, requires no locking, and is cleared on cipherdir
# unmount as a defense-in-depth measure.


class LRUCache:
    """
    Process-local LRU cache keyed by file_id that stores decoded
    thumbnail bytes. Eviction is driven by total byte size so that
    large thumbnails do not crowd out many small ones.

    Not thread-safe by design — the application runs a single asyncio
    worker, so all access is serialized on the event loop.
    """

    def __init__(self, max_bytes: int) -> None:
        self._max_bytes = max_bytes
        self._store: OrderedDict[int, tuple[str, bytes]] = OrderedDict()
        self._current_bytes: int = 0

    def get(self, file_id: int) -> tuple[str, bytes] | None:
        """
        Return (mimetype, data) for a cached thumbnail, promoting the
        entry to most-recently-used. Return None on a cache miss.
        """
        entry = self._store.get(file_id)
        if entry is None:
            return None
        self._store.move_to_end(file_id)
        return entry

    def put(self, file_id: int, mimetype: str, data: bytes) -> None:
        """
        Store (mimetype, data) for file_id. Silently discards the entry
        when the item alone exceeds the byte limit or the limit is zero.
        Evicts least-recently-used entries until the new item fits.
        """
        if self._max_bytes <= 0:
            return

        entry_size = len(data)
        if entry_size > self._max_bytes:
            return

        if file_id in self._store:
            self._current_bytes -= len(self._store[file_id][1])
            del self._store[file_id]

        while self._current_bytes + entry_size > self._max_bytes:
            _, (_, evicted_data) = self._store.popitem(last=False)
            self._current_bytes -= len(evicted_data)

        self._store[file_id] = (mimetype, data)
        self._current_bytes += entry_size

    def evict(self, file_id: int) -> None:
        """Remove the cached entry for file_id. No-op when not present."""
        entry = self._store.pop(file_id, None)
        if entry is not None:
            self._current_bytes -= len(entry[1])

    def evict_all(self) -> None:
        """Clear all cached entries."""
        self._store.clear()
        self._current_bytes = 0

    @property
    def count(self) -> int:
        return len(self._store)

    @property
    def current_bytes(self) -> int:
        return self._current_bytes

    @property
    def max_bytes(self) -> int:
        return self._max_bytes


@lru_cache(maxsize=1)
def get_thumbnail_cache() -> LRUCache:
    """
    Return the process-wide thumbnail cache singleton. Initialised on
    first call so that get_config() is not invoked at module import time
    (consistent with the ADR constraint).
    """
    return LRUCache(max_bytes=get_config().LRU_CACHE_MAX_BYTES)
