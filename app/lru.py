"""
The module contains a class for loading files using LRU cache.
"""

from collections import OrderedDict
from app.managers.file_manager import FileManager
from app.helpers.encrypt_helper import decrypt_bytes


class LRU:
    def __init__(self, cache_size: int):
        """
        Initializes the LRU class with the defined cache size.
        """
        self.cache_size = cache_size
        self.cache = OrderedDict()

    async def load(self, path: str):
        """
        Loads and decrypts an encrypted static file from the specified
        path and saves it in the LRU cache. If the file is in the cache
        the next time it is loaded, it is taken directly from there.
        When the LRU cache is full, the data in it is shifted.
        """
        if not await FileManager.file_exists(path):
            return None

        if path in self.cache:
            self.cache.move_to_end(path)
            return self.cache[path]

        encrypted_data = await FileManager.read(path)
        data = decrypt_bytes(encrypted_data)

        if len(self.cache) >= self.cache_size:
            self.cache.popitem(last=False)

        self.cache[path] = data
        return data
