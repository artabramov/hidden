# tests/schemas/test_file_tag_path.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.file_tag_path import FileTagPath


class TestFileTagPath(unittest.TestCase):

    def test_accepts_all_fields(self):
        req = FileTagPath(file_id=1, tag="important123")

        self.assertEqual(req.file_id, 1)
        self.assertEqual(req.tag, "important123")

    def test_strips_whitespace(self):
        req = FileTagPath(file_id=1, tag="  important123  ")

        self.assertEqual(req.tag, "important123")

    def test_normalizes_uppercase_letters(self):
        req = FileTagPath(file_id=1, tag="Important123")

        self.assertEqual(req.tag, "important123")

    def test_accepts_non_latin_letters(self):
        req = FileTagPath(file_id=1, tag="метка123")

        self.assertEqual(req.tag, "метка123")

    def test_file_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagPath(tag="important123")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("file_id",))
        self.assertEqual(error["type"], "missing")

    def test_tag_required(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagPath(file_id=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "missing")

    def test_file_id_must_be_positive(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagPath(file_id=0, tag="important123")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("file_id",))
        self.assertEqual(error["type"], "greater_than")

    def test_tag_too_short_after_stripping(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagPath(file_id=1, tag="   ")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "string_too_short")

    def test_tag_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagPath(file_id=1, tag="a" * 65)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "string_too_long")

    def test_rejects_spaces(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagPath(file_id=1, tag="invalid tag")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "value_not_alphanumeric_extended")

    def test_accepts_underscore(self):
        req = FileTagPath(file_id=1, tag="important_tag")

        self.assertEqual(req.tag, "important_tag")

    def test_accepts_hyphen(self):
        req = FileTagPath(file_id=1, tag="important-tag")

        self.assertEqual(req.tag, "important-tag")

    def test_rejects_special_characters(self):
        with self.assertRaises(ValidationError) as cm:
            FileTagPath(file_id=1, tag="invalid@tag")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("tag",))
        self.assertEqual(error["type"], "value_not_alphanumeric_extended")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileTagPath(file_id=1, tag="important123", other=1)

    def test_accepts_mixed_valid_characters(self):
        req = FileTagPath(file_id=1, tag="Важная_Tag-123")

        self.assertEqual(req.tag, "важная_tag-123")
