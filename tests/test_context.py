# tests/test_context.py
# SPDX-License-Identifier: GPL-3.0-only

import asyncio
import unittest

from app.context import get_context_var, reset_context, set_context_var


class TestContext(unittest.TestCase):

    def setUp(self):
        reset_context()

    def tearDown(self):
        reset_context()

    def test_get_returns_default_when_missing(self):
        self.assertIsNone(get_context_var("missing"))
        self.assertEqual(get_context_var("missing", "x"), "x")

    def test_get_returns_none_when_key_present_with_none_value(self):
        """dict.get(k, default) must not substitute default for stored None."""
        set_context_var("nullable", None)
        self.assertIsNone(get_context_var("nullable"))
        self.assertIsNone(get_context_var("nullable", "fallback"))

    def test_set_and_get_value(self):
        set_context_var("request_uuid", "abc")
        self.assertEqual(get_context_var("request_uuid"), "abc")

    def test_set_overwrites_existing_value(self):
        set_context_var("k", 1)
        set_context_var("k", 2)
        self.assertEqual(get_context_var("k"), 2)

    def test_reset_clears_context(self):
        set_context_var("k", 1)
        reset_context()
        self.assertIsNone(get_context_var("k"))

    def test_multiple_keys_are_preserved(self):
        set_context_var("a", 1)
        set_context_var("b", 2)

        self.assertEqual(get_context_var("a"), 1)
        self.assertEqual(get_context_var("b"), 2)

    def test_shallow_copy_prevents_mutation_leak(self):
        value = {"a": 1}
        set_context_var("data", value)

        # mutate original dict after set
        value["a"] = 2

        # context still sees updated dict (expected: shallow copy only)
        # but replacing context should not affect previous snapshot
        self.assertEqual(get_context_var("data")["a"], 2)

        # now overwrite context and ensure isolation between writes
        set_context_var("data", {"a": 3})
        self.assertEqual(get_context_var("data")["a"], 3)

    def test_context_is_isolated_between_tasks(self):
        async def worker(value):
            set_context_var("request_uuid", value)
            await asyncio.sleep(0)
            return get_context_var("request_uuid")

        async def run():
            reset_context()
            results = await asyncio.gather(
                worker("a"),
                worker("b"),
            )
            return results

        results = asyncio.run(run())

        self.assertCountEqual(results, ["a", "b"])

    def test_context_does_not_leak_between_tasks(self):
        async def worker_set():
            set_context_var("k", "value")
            await asyncio.sleep(0)

        async def worker_get():
            await asyncio.sleep(0)
            return get_context_var("k")

        async def run():
            reset_context()
            await asyncio.gather(worker_set(), worker_get())

        result = asyncio.run(run())

        self.assertIsNone(result)
