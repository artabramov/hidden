# tests/schemas/test_file_tag_add.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from pydantic import ValidationError

from app.schemas.file_tag_add import (
    FILE_TAG_ADD_ERRORS,
    FileTagAddRequest,
)


class TestFileTagAddRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = FileTagAddRequest(tag="important123")

        self.assertEqual(req.tag, "important123")

    def test_strips_whitespace(self):
        req = FileTagAddRequest(tag="  important123  ")

        self.assertEqual(req.tag, "important123")

    def test_normalizes_uppercase_letters(self):
        req = FileTagAddRequest(tag="Important123")

        self.assertEqual(req.tag, "important123")

    def test_accepts_non_latin_letters(self):
        req = FileTagAddRequest(tag="метка123")

        self.assertEqual(req.tag, "метка123")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileTagAddRequest(tag="important123", other=1)

    def test_tag_required(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagAddRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "missing")

    def test_tag_too_short_after_stripping(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagAddRequest(tag="   ")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "string_too_short")

    def test_tag_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagAddRequest(tag=("a" * 65))

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "string_too_long")

    def test_rejects_spaces(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagAddRequest(tag="invalid tag")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "value_not_alphanumeric_extended")

    def test_accepts_underscore(self):
        req = FileTagAddRequest(tag="important_tag")

        self.assertEqual(req.tag, "important_tag")

    def test_accepts_hyphen(self):
        req = FileTagAddRequest(tag="important-tag")

        self.assertEqual(req.tag, "important-tag")

    def test_accepts_mixed_valid_characters(self):
        req = FileTagAddRequest(tag="Важная_Tag-123")

        self.assertEqual(req.tag, "важная_tag-123")

    def test_rejects_special_characters(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagAddRequest(tag="invalid@tag")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "value_not_alphanumeric_extended")

    def test_accepts_only_underscore(self):
        req = FileTagAddRequest(tag="_")

        self.assertEqual(req.tag, "_")

    def test_accepts_only_hyphen(self):
        req = FileTagAddRequest(tag="-")

        self.assertEqual(req.tag, "-")

    def test_rejects_mixed_with_space(self):
        with self.assertRaises(ValidationError):
            FileTagAddRequest(tag="valid_tag invalid")

    def test_rejects_mixed_with_special_char(self):
        with self.assertRaises(ValidationError):
            FileTagAddRequest(tag="valid-tag@123")

    def test_preserves_unicode_letters_with_symbols(self):
        req = FileTagAddRequest(tag="Метка_Тест-123")

        self.assertEqual(req.tag, "метка_тест-123")

    def test_rejects_newline(self):
        with self.assertRaises(ValidationError):
            FileTagAddRequest(tag="invalid\n_tag")


class TestFileTagAddErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(FILE_TAG_ADD_ERRORS),
            {401, 403, 404, 422, 423, 503},
        )
