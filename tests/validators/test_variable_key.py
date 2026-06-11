# tests/validators/test_variable_key.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from pydantic_core import PydanticCustomError

from app.validators.variable_key import validate_variable_key


class TestValidateVariableKey(unittest.TestCase):
    def test_returns_value_for_non_string(self):
        value = 123
        result = validate_variable_key(value)
        self.assertEqual(result, value)

    def test_returns_empty_string_as_is(self):
        value = ""
        result = validate_variable_key(value)
        self.assertEqual(result, value)

    def test_accepts_valid_key(self):
        value = "valid_key-123"
        result = validate_variable_key(value)
        self.assertEqual(result, value)

    def test_rejects_uppercase_letters(self):
        with self.assertRaises(PydanticCustomError):
            validate_variable_key("Invalid")

    def test_rejects_spaces(self):
        with self.assertRaises(PydanticCustomError):
            validate_variable_key("invalid key")

    def test_rejects_special_characters(self):
        with self.assertRaises(PydanticCustomError):
            validate_variable_key("invalid@key")

    def test_rejects_mixed_invalid_characters(self):
        with self.assertRaises(PydanticCustomError):
            validate_variable_key("Key-123!")
