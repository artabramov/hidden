"""
The module contains a class for loading files using LRU cache.
"""

from collections import OrderedDict


class LRU:
    def __init__(self, cache_size: int):
        """
        Initializes the LRU class with a maximum number of cached
        entities.
        """
        self.cache_size = cache_size
        self.cache: OrderedDict[int, bytes] = OrderedDict()

    async def save(self, key: str, value: bytes):
        """
        Saves the given decrypted data in the cache under the given key.
        If the cache exceeds the limit, the least recently used item is
        evicted.
        """
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)

    async def load(self, key: str) -> bytes | None:
        """
        Loads and returns decrypted data from the cache by key.
        If the key is not in the cache, returns None.
        """
        if key not in self.cache:
            return None

        self.cache.move_to_end(key)
        return self.cache[key]
