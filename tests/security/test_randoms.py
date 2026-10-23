# tests/security/test_randoms.py
# SPDX-License-Identifier: Apache-2.0

import string
import unittest
from unittest.mock import call, patch

from app.security.randoms import _ALPHABET, generate_random_string


class TestGenerateRandomString(unittest.TestCase):
    def test_rejects_non_positive_length(self):
        for length in (0, -1):
            with self.subTest(length=length):
                with self.assertRaises(ValueError) as caught:
                    generate_random_string(length)

                self.assertEqual(
                    str(caught.exception),
                    "length must be positive",
                )

    def test_draws_each_character_from_the_alphabet(self):
        self.assertEqual(
            _ALPHABET,
            string.ascii_letters + string.digits,
        )

        with patch(
            "app.security.randoms.secrets.choice",
            return_value="Z",
        ) as choice:
            result = generate_random_string(4)

        self.assertEqual(result, "ZZZZ")
        self.assertEqual(choice.call_args_list, [call(_ALPHABET)] * 4)

    def test_returns_requested_length(self):
        for length in (1, 20):
            with self.subTest(length=length):
                result = generate_random_string(length)

            self.assertEqual(len(result), length)
            self.assertTrue(set(result).issubset(_ALPHABET))
