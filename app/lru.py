"""
Implements an in-memory least recently used (LRU) cache for storing
decrypted file data with automatic eviction of the oldest entries
when the cache exceeds the configured size.
"""

from collections import OrderedDict


class LRU:
    def __init__(self, cache_size: int):
        """
        Initializes the cache with a maximum number of entities that
        can be stored before eviction occurs.
        """
        self.cache_size = cache_size
        self.cache: OrderedDict[int, bytes] = OrderedDict()

    async def save(self, key: str, value: bytes):
        """
        Stores the given value under the specified key, updates its
        position as most recently used and evicts the oldest entry if
        the cache exceeds its capacity.
        """
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)

    async def load(self, key: str) -> bytes | None:
        """
        Retrieves the value associated with the specified key, returns
        None if it is not present, and marks it as most recently used.
        """
        if key not in self.cache:
            return None

        self.cache.move_to_end(key)
        return self.cache[key]
