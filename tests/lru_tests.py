import unittest
from app.lru import LRU


class LruTests(unittest.TestCase):

    def test_save_under_capacity_no_eviction(self):
        # capacity is in BYTES; each value is 1 byte
        lru = LRU(3)
        lru.save("a", b"A")
        lru.save("b", b"B")
        lru.save("c", b"C")
        self.assertEqual(list(lru.cache.keys()), ["a", "b", "c"])
        self.assertEqual(lru.size, 3)
        self.assertEqual(lru.count, 3)

    def test_load_hit_moves_to_mru(self):
        lru = LRU(3)
        lru.save("a", b"A")
        lru.save("b", b"B")
        lru.save("c", b"C")
        val = lru.load("b")
        self.assertEqual(val, b"B")
        self.assertEqual(list(lru.cache.keys()), ["a", "c", "b"])

    def test_load_miss_returns_none_no_reorder(self):
        lru = LRU(2)
        lru.save("x", b"X")
        lru.save("y", b"Y")
        val = lru.load("z")
        self.assertIsNone(val)
        self.assertEqual(list(lru.cache.keys()), ["x", "y"])

    def test_save_existing_overwrites_and_moves(self):
        # Total size after overwrite: len("A2")=2 + "B"(1) + "C"(1) = 4 bytes.
        # Set capacity to 4 so nothing is evicted.
        lru = LRU(4)
        lru.save("a", b"A1")
        lru.save("b", b"B")
        lru.save("c", b"C")
        lru.save("a", b"A2")  # overwrite -> move to MRU
        self.assertEqual(list(lru.cache.keys()), ["b", "c", "a"])
        self.assertEqual(lru.cache["a"], b"A2")
        self.assertEqual(lru.size, 4)

    def test_eviction_drops_lru(self):
        lru = LRU(2)
        lru.save("a", b"A")
        lru.save("b", b"B")
        lru.save("c", b"C")  # should evict "a"
        self.assertEqual(list(lru.cache.keys()), ["b", "c"])
        self.assertNotIn("a", lru.cache)
        self.assertEqual(lru.size, 2)

    def test_size_one_behaviour(self):
        lru = LRU(1)
        lru.save("a", b"A")
        self.assertEqual(list(lru.cache.keys()), ["a"])
        lru.save("b", b"B")  # evicts "a"
        self.assertEqual(list(lru.cache.keys()), ["b"])
        self.assertIsNone(lru.load("a"))
        self.assertEqual(lru.load("b"), b"B")
        self.assertEqual(lru.size, 1)
        self.assertEqual(lru.count, 1)

    def test_oversize_item_skipped_when_new(self):
        # item_size_bytes = 3, attempting to save 4 bytes -> skipped
        lru = LRU(cache_size_bytes=10, item_size_bytes=3)
        lru.save("big", b"XXXX")  # 4 bytes
        self.assertEqual(list(lru.cache.keys()), [])
        self.assertIsNone(lru.load("big"))
        self.assertEqual(lru.size, 0)
        self.assertEqual(lru.count, 0)

    def test_oversize_update_removes_existing(self):
        # Put small, then update with oversize -> key is removed
        lru = LRU(cache_size_bytes=10, item_size_bytes=3)
        lru.save("k", b"ok")      # 2 bytes
        self.assertEqual(list(lru.cache.keys()), ["k"])
        lru.save("k", b"toolong")  # 7 bytes > 3 -> remove existing
        self.assertEqual(list(lru.cache.keys()), [])
        self.assertIsNone(lru.load("k"))
        self.assertEqual(lru.size, 0)

    def test_eviction_by_total_bytes_var_lengths(self):
        lru = LRU(5)  # 5 bytes total
        lru.save("a", b"AA")   # size=2
        lru.save("b", b"BBB")  # size=5
        self.assertEqual(list(lru.cache.keys()), ["a", "b"])
        self.assertEqual(lru.size, 5)

        # Adding 1 byte exceeds cap -> evict from front until <= 5
        lru.save("c", b"C")    # would be 6 -> evict "a" (2)
        self.assertEqual(list(lru.cache.keys()), ["b", "c"])
        self.assertNotIn("a", lru.cache)
        self.assertEqual(lru.size, 4)

    def test_update_existing_moves_to_mru_same_size(self):
        lru = LRU(3)
        lru.save("a", b"A")
        lru.save("b", b"B")
        lru.save("c", b"C")
        lru.save("b", b"Z")  # same length, should just move to MRU
        self.assertEqual(list(lru.cache.keys()), ["a", "c", "b"])
        self.assertEqual(lru.cache["b"], b"Z")

    def test_delete_existing_removes_and_updates_size(self):
        lru = LRU(5)
        lru.save("a", b"AA")    # 2
        lru.save("b", b"BBB")   # +3 => 5
        lru.delete("a")
        self.assertEqual(list(lru.cache.keys()), ["b"])
        self.assertEqual(lru.size, 3)
        self.assertEqual(lru.count, 1)
        self.assertIsNone(lru.load("a"))
        self.assertEqual(lru.load("b"), b"BBB")

    def test_delete_nonexistent_noop(self):
        lru = LRU(3)
        lru.save("a", b"A")
        lru.save("b", b"B")
        lru.save("c", b"C")
        lru.delete("z")  # no-op
        self.assertEqual(list(lru.cache.keys()), ["a", "b", "c"])
        self.assertEqual(lru.size, 3)
        self.assertEqual(lru.count, 3)

    def test_delete_mru_and_lru(self):
        lru = LRU(3)
        lru.save("a", b"A")
        lru.save("b", b"B")
        lru.save("c", b"C")  # order: ["a","b","c"]
        lru.delete("c")      # delete MRU
        self.assertEqual(list(lru.cache.keys()), ["a", "b"])
        lru.delete("a")      # delete LRU
        self.assertEqual(list(lru.cache.keys()), ["b"])
        self.assertEqual(lru.size, 1)

    def test_delete_then_readd_adds_as_mru(self):
        lru = LRU(3)
        lru.save("a", b"A")
        lru.save("b", b"B")
        lru.delete("a")
        self.assertEqual(list(lru.cache.keys()), ["b"])
        lru.save("a", b"A")  # re-add -> should be MRU
        self.assertEqual(list(lru.cache.keys()), ["b", "a"])

    def test_delete_can_prevent_future_eviction(self):
        # After deleting smaller entry, adding another should fit w/o eviction.
        lru = LRU(4)
        lru.save("a", b"AA")  # 2
        lru.save("b", b"B")   # 1 -> total 3
        lru.delete("b")       # total 2
        lru.save("c", b"CC")  # +2 -> total 4 fits, no eviction
        self.assertEqual(list(lru.cache.keys()), ["a", "c"])
        self.assertEqual(lru.size, 4)

    def test_clear_empties_cache_and_resets_properties(self):
        lru = LRU(10)
        lru.save("a", b"AA")
        lru.save("b", b"BBB")
        self.assertGreater(lru.size, 0)
        self.assertGreater(lru.count, 0)
        lru.clear()
        self.assertEqual(list(lru.cache.keys()), [])
        self.assertEqual(lru.size, 0)
        self.assertEqual(lru.count, 0)

    def test_overwrite_longer_triggers_eviction(self):
        lru = LRU(4)
        lru.save("a", b"A")   # 1
        lru.save("b", b"B")   # 1 -> total 2
        lru.save("c", b"C")   # 1 -> total 3; order: ["a","b","c"]

        lru.save("b", b"BBBB")

        self.assertEqual(list(lru.cache.keys()), ["b"])
        self.assertEqual(lru.load("b"), b"BBBB")
        self.assertEqual(lru.size, 4)
        self.assertEqual(lru.count, 1)
