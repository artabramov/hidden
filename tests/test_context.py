# tests/test_context.py
# SPDX-License-Identifier: Apache-2.0

import unittest

from app.context import (
    _context,
    get_context_var,
    reset_context,
    set_context_var,
)


class TestContext(unittest.TestCase):
    def setUp(self):
        reset_context()

    def tearDown(self):
        reset_context()

    def test_returns_default_when_name_is_missing(self):
        self.assertIsNone(get_context_var("missing"))
        self.assertEqual(get_context_var("missing", "-"), "-")

    def test_stores_values_without_changing_earlier_mapping(self):
        set_context_var("request_uuid", "abc")
        first = _context.get()
        set_context_var("other", 1)
        second = _context.get()

        self.assertEqual(get_context_var("request_uuid"), "abc")
        self.assertEqual(get_context_var("other"), 1)
        self.assertIsNot(first, second)
        self.assertEqual(first, {"request_uuid": "abc"})
        self.assertEqual(second, {"request_uuid": "abc", "other": 1})

    def test_reset_clears_values(self):
        set_context_var("request_uuid", "abc")
        reset_context()

        self.assertIsNone(get_context_var("request_uuid"))
        self.assertEqual(get_context_var("request_uuid", "-"), "-")
