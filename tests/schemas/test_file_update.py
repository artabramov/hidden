# tests/schemas/test_file_update.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.schemas.file_update import FileUpdateRequest, FileUpdateResponse


class TestFileUpdateRequest(unittest.TestCase):

    def test_accepts_valid_payload_with_summary(self):
        req = FileUpdateRequest(
            filename="document.txt",
            summary="File summary.",
        )

        self.assertEqual(req.filename, "document.txt")
        self.assertEqual(req.summary, "File summary.")

    def test_accepts_valid_payload_without_summary(self):
        req = FileUpdateRequest(
            filename="document.txt",
        )

        self.assertEqual(req.filename, "document.txt")
        self.assertIsNone(req.summary)

    def test_accepts_none_summary(self):
        req = FileUpdateRequest(
            filename="document.txt",
            summary=None,
        )

        self.assertEqual(req.filename, "document.txt")
        self.assertIsNone(req.summary)

    def test_strips_whitespace(self):
        req = FileUpdateRequest(
            filename="  document.txt  ",
            summary="  File summary.  ",
        )

        self.assertEqual(req.filename, "document.txt")
        self.assertEqual(req.summary, "File summary.")

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(
                filename="document.txt",
                summary="File summary.",
                other=1,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_filename(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(
                summary="File summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "missing")

    def test_rejects_filename_too_short_after_stripping(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(
                filename="   ",
                summary="File summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "string_too_short")

    def test_rejects_filename_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(
                filename=("a" * 256),
                summary="File summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "string_too_long")

    def test_rejects_summary_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(
                filename="document.txt",
                summary=("a" * 4097),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("summary",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_empty_string_normalized_to_none(self):
        req = FileUpdateRequest(
            filename="document.txt",
            summary="",
        )

        self.assertIsNone(req.summary)

    def test_summary_whitespace_only_normalized_to_none(self):
        req = FileUpdateRequest(
            filename="document.txt",
            summary="   ",
        )

        self.assertIsNone(req.summary)

    def test_accepts_filename_with_extension(self):
        req = FileUpdateRequest(
            filename="document.txt",
            summary=None,
        )

        self.assertEqual(req.filename, "document.txt")

    def test_accepts_filename_with_inner_dots(self):
        req = FileUpdateRequest(
            filename="archive.tar.gz",
            summary=None,
        )

        self.assertEqual(req.filename, "archive.tar.gz")

    def test_accepts_filename_with_leading_dot_when_not_dot_segment(self):
        req = FileUpdateRequest(
            filename=".env",
            summary=None,
        )

        self.assertEqual(req.filename, ".env")

    def test_rejects_dot_filename(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(filename=".", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_double_dot_filename(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(filename="..", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_forward_slash_in_filename(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(filename="foo/bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_backslash_in_filename(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(filename="foo\\bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_null_byte_in_filename(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(filename="foo\x00bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_control_character_in_filename(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateRequest(filename="foo\nbar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("filename",))
        self.assertEqual(error["type"], "value_not_path_segment")


class TestFileUpdateResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileUpdateResponse(id=1)

        self.assertEqual(resp.file_id, 1)

    def test_accepts_valid_payload_by_field_name(self):
        resp = FileUpdateResponse(file_id=1)

        self.assertEqual(resp.file_id, 1)

    def test_accepts_object_from_attributes(self):
        file = MagicMock()
        file.id = 1

        resp = FileUpdateResponse.model_validate(file)

        self.assertEqual(resp.file_id, 1)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateResponse(id=1, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_file_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileUpdateResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")
