import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from collections import OrderedDict
from app.lru import LRU


class LRUTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.lru.FileManager", new_callable=AsyncMock)
    async def test_file_not_found(self, FileManagerMock):
        FileManagerMock.file_exists.return_value = False

        lru = LRU(10)
        result = await lru.load("/path")

        self.assertIsNone(result)
        FileManagerMock.file_exists.assert_called_with("/path")

    @patch("app.lru.FileManager", new_callable=AsyncMock)
    async def test_file_in_cache(self, FileManagerMock):
        FileManagerMock.file_exists.return_value = True

        lru = LRU(10)
        lru.cache = MagicMock(spec=OrderedDict)

        lru.cache.__contains__.side_effect = lambda path: path == "/path"
        lru.cache.__getitem__.return_value = b"cached-data"

        result = await lru.load("/path")

        self.assertEqual(result, b"cached-data")
        FileManagerMock.file_exists.assert_called_with("/path")
        lru.cache.move_to_end.assert_called_with("/path")

    @patch("app.lru.decrypt_bytes")
    @patch("app.lru.FileManager", new_callable=AsyncMock)
    async def test_file_not_in_cache(self, FileManagerMock,
                                     decrypt_bytes_mock):
        FileManagerMock.file_exists.return_value = True
        FileManagerMock.read.return_value = b"encrypted-data"
        decrypt_bytes_mock.return_value = b"decrypted-data"

        lru = LRU(10)

        lru.cache = MagicMock(spec=OrderedDict)
        lru.cache.__contains__.side_effect = lambda path: False

        result = await lru.load("/path")

        self.assertEqual(result, b"decrypted-data")
        FileManagerMock.file_exists.assert_called_with("/path")
        FileManagerMock.read.assert_called_with("/path")
        decrypt_bytes_mock.assert_called_with(b"encrypted-data")
        lru.cache.__setitem__.assert_called_with("/path", b"decrypted-data")
        lru.cache.move_to_end.assert_not_called()

    @patch("app.lru.decrypt_bytes")
    @patch("app.lru.FileManager", new_callable=AsyncMock)
    async def test_lru_eviction(self, FileManagerMock, decrypt_bytes_mock):
        lru_cache = OrderedDict()

        FileManagerMock.file_exists.return_value = True
        FileManagerMock.read.side_effect = [
            b"encrypted-data-1", b"encrypted-data-2", b"encrypted-data-3"
        ]

        decrypt_bytes_mock.side_effect = [
            b"decrypted-data-1", b"decrypted-data-2", b"decrypted-data-3"
        ]

        lru = LRU(2)

        lru.cache = lru_cache

        result1 = await lru.load("/path1")
        result2 = await lru.load("/path2")
        result3 = await lru.load("/path3")

        self.assertEqual(result1, b"decrypted-data-1")
        self.assertEqual(result2, b"decrypted-data-2")
        self.assertEqual(result3, b"decrypted-data-3")

        self.assertIn("/path2", lru_cache)
        self.assertIn("/path3", lru_cache)
        self.assertNotIn("/path1", lru_cache)

        self.assertEqual(len(lru_cache), 2)

        FileManagerMock.read.assert_any_call("/path1")
        FileManagerMock.read.assert_any_call("/path2")
        FileManagerMock.read.assert_any_call("/path3")
        decrypt_bytes_mock.assert_any_call(b"encrypted-data-1")
        decrypt_bytes_mock.assert_any_call(b"encrypted-data-2")
        decrypt_bytes_mock.assert_any_call(b"encrypted-data-3")


if __name__ == "__main__":
    unittest.main()
