# tests/security/test_randoms.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
import string

from app.security import randoms


class TestRandoms(unittest.TestCase):
    def test_generate_random_string_raises_when_length_zero(self):
        with self.assertRaises(ValueError) as cm:
            randoms.generate_random_string(0)

        self.assertEqual(str(cm.exception), "length must be positive")

    def test_generate_random_string_raises_when_length_negative(self):
        with self.assertRaises(ValueError):
            randoms.generate_random_string(-1)

    def test_generate_random_string_returns_correct_length(self):
        result = randoms.generate_random_string(32)

        self.assertEqual(len(result), 32)

    def test_generate_random_string_uses_expected_alphabet(self):
        alphabet = string.ascii_letters + string.digits

        result = randoms.generate_random_string(1000)

        for ch in result:
            self.assertIn(ch, alphabet)

    def test_generate_random_string_returns_different_values(self):
        s1 = randoms.generate_random_string(32)
        s2 = randoms.generate_random_string(32)

        self.assertNotEqual(s1, s2)

    def test_generate_random_string_length_one(self):
        result = randoms.generate_random_string(1)

        self.assertEqual(len(result), 1)

    def test_generate_random_string_large_length(self):
        result = randoms.generate_random_string(10_000)

        self.assertEqual(len(result), 10_000)
