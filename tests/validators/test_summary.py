# tests/validators/test_summary.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.validators.summary import normalize_summary


class TestNormalizeSummary(unittest.TestCase):
    def test_returns_none_for_empty_string(self):
        result = normalize_summary("")
        self.assertIsNone(result)

    def test_returns_none_for_none(self):
        result = normalize_summary(None)
        self.assertIsNone(result)

    def test_returns_same_value_for_non_empty_string(self):
        value = "Some summary"
        result = normalize_summary(value)
        self.assertEqual(result, value)

    def test_preserves_whitespace_string(self):
        value = "   "
        result = normalize_summary(value)
        self.assertEqual(result, value)
