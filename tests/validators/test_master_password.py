# tests/validators/test_master_password.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from pydantic_core import PydanticCustomError

from app.validators.master_password import (
    validate_master_password,
)


class TestValidateMasterPassword(unittest.TestCase):
    def test_rejects_missing_lowercase(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_master_password("PASSWORD123")

        self.assertEqual(cm.exception.type, "value_missing_lowercase")

    def test_rejects_missing_uppercase(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_master_password("password123")

        self.assertEqual(cm.exception.type, "value_missing_uppercase")

    def test_rejects_missing_digit(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_master_password("Password")

        self.assertEqual(cm.exception.type, "value_missing_digit")

    def test_rejects_predictable_sequence_numeric(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_master_password("Abc0123X")

        self.assertEqual(cm.exception.type, "value_error")

    def test_rejects_predictable_sequence_keyboard(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_master_password("Qwer123A")

        self.assertEqual(cm.exception.type, "value_error")

    def test_rejects_repeated_characters(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_master_password("Aa111bcD")

        self.assertEqual(cm.exception.type, "value_error")

    def test_rejects_common_weak_fragment(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_master_password("Password1A")

        self.assertEqual(cm.exception.type, "value_error")

    def test_accepts_valid_strong_password(self):
        value = "A9x$kL2pQ"

        result = validate_master_password(value)

        self.assertEqual(result, value)

    def test_detects_sequence_case_insensitive(self):
        with self.assertRaises(PydanticCustomError):
            validate_master_password("Abcdef1X")  # contains abcdef

    def test_detects_fragment_case_insensitive(self):
        with self.assertRaises(PydanticCustomError):
            validate_master_password("MyAdmin123A")  # contains admin
