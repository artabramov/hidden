# tests/validators/test_password.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from pydantic_core import PydanticCustomError

from app.validators.password import validate_password


class TestValidatePassword(unittest.TestCase):
    def test_rejects_missing_lowercase(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_password("PASSWORD123")

        self.assertEqual(cm.exception.type, "value_missing_lowercase")

    def test_rejects_missing_uppercase(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_password("password123")

        self.assertEqual(cm.exception.type, "value_missing_uppercase")

    def test_rejects_missing_digit(self):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_password("Password")

        self.assertEqual(cm.exception.type, "value_missing_digit")

    def test_accepts_valid_password(self):
        value = "Password123"

        result = validate_password(value)

        self.assertEqual(result, value)

    def test_accepts_minimal_valid_combination(self):
        value = "A1a"

        result = validate_password(value)

        self.assertEqual(result, value)
