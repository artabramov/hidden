# tests/security/test_hashing.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.security import hashing


class TestHashing(unittest.TestCase):
    def test_hash_string_returns_valid_format(self):
        result = hashing.hash_string("password")

        parts = result.split("$")
        self.assertEqual(len(parts), 3)

        iterations, salt_hex, hash_hex = parts

        self.assertEqual(int(iterations), 600_000)
        self.assertEqual(len(bytes.fromhex(salt_hex)), 16)
        self.assertGreater(len(hash_hex), 0)

    def test_hash_string_produces_different_hashes_for_same_password(
        self,
    ):
        h1 = hashing.hash_string("password")
        h2 = hashing.hash_string("password")

        self.assertNotEqual(h1, h2)

    def test_is_password_correct_returns_true_for_valid_password(
        self,
    ):
        password = "secret"
        password_hash = hashing.hash_string(password)

        result = hashing.is_password_correct(
            password,
            password_hash,
        )

        self.assertTrue(result)

    def test_is_password_correct_returns_false_for_invalid_password(
        self,
    ):
        password_hash = hashing.hash_string("correct")

        result = hashing.is_password_correct(
            "wrong",
            password_hash,
        )

        self.assertFalse(result)

    def test_is_password_correct_returns_false_for_invalid_format(
        self,
    ):
        result = hashing.is_password_correct(
            "password",
            "invalid-format",
        )

        self.assertFalse(result)

    def test_is_password_correct_returns_false_for_corrupted_hash(
        self,
    ):
        password = "secret"
        password_hash = hashing.hash_string(password)

        parts = password_hash.split("$")
        corrupted_hash = f"{parts[0]}${parts[1]}$deadbeef"

        result = hashing.is_password_correct(
            password,
            corrupted_hash,
        )

        self.assertFalse(result)

    def test_is_password_correct_respects_iterations_from_hash(
        self,
    ):
        password = "secret"
        password_hash = hashing.hash_string(password)

        iterations, salt_hex, hash_hex = password_hash.split("$")
        modified = f"{int(iterations) - 1}${salt_hex}${hash_hex}"

        result = hashing.is_password_correct(
            password,
            modified,
        )

        self.assertFalse(result)

    def test_is_password_correct_returns_false_for_invalid_hex(
        self,
    ):
        password_hash = "600000$nothex$nothex"

        result = hashing.is_password_correct(
            "password",
            password_hash,
        )

        self.assertFalse(result)
