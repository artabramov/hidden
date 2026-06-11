# tests/validators/test_file_tag.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from pydantic_core import PydanticCustomError

from app.validators.file_tag import validate_file_tag


class TestValidateFileTag(unittest.TestCase):
    def test_rejects_non_string(self):
        with self.assertRaises(PydanticCustomError):
            validate_file_tag(123)

    def test_rejects_empty_string(self):
        with self.assertRaises(PydanticCustomError):
            validate_file_tag("")

    def test_accepts_lowercase_letters(self):
        value = "important"
        result = validate_file_tag(value)
        self.assertEqual(result, value)

    def test_accepts_digits(self):
        value = "tag123"
        result = validate_file_tag(value)
        self.assertEqual(result, value)

    def test_normalizes_uppercase_letters(self):
        result = validate_file_tag("Important123")
        self.assertEqual(result, "important123")

    def test_accepts_non_latin_letters(self):
        value = "метка123"
        result = validate_file_tag(value)
        self.assertEqual(result, value)

    def test_accepts_underscore(self):
        value = "invalid_tag"
        result = validate_file_tag(value)
        self.assertEqual(result, value)

    def test_accepts_hyphen(self):
        value = "invalid-tag"
        result = validate_file_tag(value)
        self.assertEqual(result, value)

    def test_rejects_spaces(self):
        with self.assertRaises(PydanticCustomError):
            validate_file_tag("invalid tag")

    def test_rejects_special_characters(self):
        with self.assertRaises(PydanticCustomError):
            validate_file_tag("invalid@tag")

    def test_accepts_mixed_valid_characters(self):
        result = validate_file_tag("Важная_Tag-123")
        self.assertEqual(result, "важная_tag-123")
