# tests/cache/test_lru.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import patch

from app.cache.lru import LRUCache, get_thumbnail_cache


class TestLRUCache(unittest.TestCase):

    def _make(self, max_bytes: int = 1024) -> LRUCache:
        return LRUCache(max_bytes=max_bytes)

    # --- get / put ---

    def test_miss_returns_none(self):
        cache = self._make()
        self.assertIsNone(cache.get(1))

    def test_put_and_get_returns_entry(self):
        cache = self._make()
        cache.put(1, "image/jpeg", b"data")
        self.assertEqual(cache.get(1), ("image/jpeg", b"data"))

    def test_get_promotes_to_most_recent(self):
        cache = self._make(max_bytes=6)
        cache.put(1, "image/jpeg", b"aaa")
        cache.put(2, "image/png", b"bbb")
        cache.get(1)
        cache.put(3, "image/gif", b"ccc")
        self.assertIsNone(cache.get(2))
        self.assertIsNotNone(cache.get(1))
        self.assertIsNotNone(cache.get(3))

    def test_put_overwrites_existing_entry(self):
        cache = self._make()
        cache.put(1, "image/jpeg", b"old")
        cache.put(1, "image/png", b"new")
        self.assertEqual(cache.get(1), ("image/png", b"new"))

    def test_put_updates_byte_count_on_overwrite(self):
        cache = self._make()
        cache.put(1, "image/jpeg", b"abc")
        cache.put(1, "image/jpeg", b"x")
        self.assertEqual(cache.current_bytes, 1)

    # --- eviction by byte limit ---

    def test_lru_eviction_when_limit_exceeded(self):
        cache = self._make(max_bytes=6)
        cache.put(1, "image/jpeg", b"aaa")
        cache.put(2, "image/png", b"bbb")
        cache.put(3, "image/gif", b"ccc")
        self.assertIsNone(cache.get(1))
        self.assertIsNotNone(cache.get(2))
        self.assertIsNotNone(cache.get(3))

    def test_item_larger_than_limit_is_silently_dropped(self):
        cache = self._make(max_bytes=2)
        cache.put(1, "image/jpeg", b"toolong")
        self.assertIsNone(cache.get(1))
        self.assertEqual(cache.current_bytes, 0)

    def test_zero_max_bytes_disables_cache(self):
        cache = self._make(max_bytes=0)
        cache.put(1, "image/jpeg", b"data")
        self.assertIsNone(cache.get(1))
        self.assertEqual(cache.current_bytes, 0)

    def test_negative_max_bytes_disables_cache(self):
        cache = self._make(max_bytes=-1)
        cache.put(1, "image/jpeg", b"data")
        self.assertIsNone(cache.get(1))
        self.assertEqual(cache.current_bytes, 0)

    def test_current_bytes_tracks_stored_size(self):
        cache = self._make()
        cache.put(1, "image/jpeg", b"abcde")
        cache.put(2, "image/png", b"fg")
        self.assertEqual(cache.current_bytes, 7)

    # --- evict ---

    def test_evict_removes_entry(self):
        cache = self._make()
        cache.put(1, "image/jpeg", b"data")
        cache.evict(1)
        self.assertIsNone(cache.get(1))

    def test_evict_updates_byte_count(self):
        cache = self._make()
        cache.put(1, "image/jpeg", b"abc")
        cache.evict(1)
        self.assertEqual(cache.current_bytes, 0)

    def test_evict_noop_for_missing_entry(self):
        cache = self._make()
        cache.evict(99)
        self.assertEqual(cache.current_bytes, 0)

    # --- evict_all ---

    def test_evict_all_clears_cache(self):
        cache = self._make()
        cache.put(1, "image/jpeg", b"a")
        cache.put(2, "image/png", b"bb")
        cache.evict_all()
        self.assertIsNone(cache.get(1))
        self.assertIsNone(cache.get(2))
        self.assertEqual(cache.current_bytes, 0)

    def test_evict_all_on_empty_cache(self):
        cache = self._make()
        cache.evict_all()
        self.assertEqual(cache.current_bytes, 0)

    # --- properties ---

    def test_max_bytes_property(self):
        cache = self._make(max_bytes=512)
        self.assertEqual(cache.max_bytes, 512)

    def test_count_reflects_number_of_entries(self):
        cache = self._make(max_bytes=512)
        self.assertEqual(cache.count, 0)
        cache.put(1, "image/jpeg", b"a")
        self.assertEqual(cache.count, 1)
        cache.put(2, "image/png", b"bb")
        self.assertEqual(cache.count, 2)
        cache.evict(1)
        self.assertEqual(cache.count, 1)
        cache.evict_all()
        self.assertEqual(cache.count, 0)

    def test_multiple_evictions_to_fit_new_item(self):
        cache = self._make(max_bytes=6)
        cache.put(1, "image/jpeg", b"aaa")
        cache.put(2, "image/png", b"bbb")
        cache.put(3, "image/gif", b"cccccc")
        self.assertIsNone(cache.get(1))
        self.assertIsNone(cache.get(2))
        self.assertIsNotNone(cache.get(3))

    def test_overwrite_with_larger_entry_evicts_lru_if_needed(self):
        cache = self._make(max_bytes=7)
        cache.put(1, "image/jpeg", b"aaa")
        cache.put(2, "image/png", b"bb")
        cache.put(3, "image/gif", b"cc")
        cache.put(1, "image/jpeg", b"aaaa")
        self.assertEqual(cache.get(1), ("image/jpeg", b"aaaa"))
        self.assertIsNone(cache.get(2))
        self.assertEqual(cache.get(3), ("image/gif", b"cc"))
        self.assertEqual(cache.current_bytes, 6)


class TestGetThumbnailCache(unittest.TestCase):

    def tearDown(self):
        get_thumbnail_cache.cache_clear()

    def test_returns_singleton_instance(self):
        with patch("app.cache.lru.get_config") as get_config_mock:
            get_config_mock.return_value.LRU_CACHE_MAX_BYTES = 123
            first = get_thumbnail_cache()
            second = get_thumbnail_cache()
        self.assertIs(first, second)
        self.assertEqual(first.max_bytes, 123)
        get_config_mock.assert_called_once()
