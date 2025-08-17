import unittest
from app.lru import LRU


class LRUTest(unittest.IsolatedAsyncioTestCase):

    async def test_save_and_load(self):
        lru = LRU(2)
        await lru.save(1, b"data1")
        await lru.save(2, b"data2")

        result1 = await lru.load(1)
        result2 = await lru.load(2)

        self.assertEqual(result1, b"data1")
        self.assertEqual(result2, b"data2")

    async def test_lru_eviction(self):
        lru = LRU(2)
        await lru.save(1, b"data1")
        await lru.save(2, b"data2")
        await lru.load(1)
        await lru.save(3, b"data3")

        self.assertIn(1, lru.cache)
        self.assertIn(3, lru.cache)
        self.assertNotIn(2, lru.cache)

    async def test_load_not_found(self):
        lru = LRU(1)
        result = await lru.load(99)
        self.assertIsNone(result)

    async def test_update_existing_key(self):
        lru = LRU(2)
        await lru.save(1, b"data1")
        await lru.save(1, b"data1-new")

        result = await lru.load(1)
        self.assertEqual(result, b"data1-new")

        self.assertEqual(list(lru.cache.keys())[-1], 1)


if __name__ == "__main__":
    unittest.main()
