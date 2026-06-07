# tests/validators/test_variable_namespace.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from pydantic_core import PydanticCustomError

from app.validators.variable_namespace import validate_namespace


class TestValidateNamespace(unittest.TestCase):
    def test_returns_value_for_non_string(self):
        value = 123
        result = validate_namespace(value)
        self.assertEqual(result, value)

    def test_returns_empty_string_as_is(self):
        value = ""
        result = validate_namespace(value)
        self.assertEqual(result, value)

    def test_accepts_valid_namespace(self):
        value = "valid_namespace-123"
        result = validate_namespace(value)
        self.assertEqual(result, value)

    def test_rejects_uppercase_letters(self):
        with self.assertRaises(PydanticCustomError):
            validate_namespace("Invalid")

    def test_rejects_spaces(self):
        with self.assertRaises(PydanticCustomError):
            validate_namespace("invalid namespace")

    def test_rejects_special_characters(self):
        with self.assertRaises(PydanticCustomError):
            validate_namespace("invalid@namespace")

    def test_rejects_mixed_invalid_characters(self):
        with self.assertRaises(PydanticCustomError):
            validate_namespace("Namespace-123!")
