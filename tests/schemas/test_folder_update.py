# tests/schemas/test_folder_update.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.folder_update import FolderUpdateRequest


class TestFolderUpdateRequest(unittest.TestCase):

    def test_accepts_valid_payload_with_summary(self):
        req = FolderUpdateRequest(
            dirname="documents",
            summary="Folder summary.",
        )

        self.assertEqual(req.dirname, "documents")
        self.assertEqual(req.summary, "Folder summary.")

    def test_accepts_valid_payload_without_summary(self):
        req = FolderUpdateRequest(
            dirname="documents",
        )

        self.assertEqual(req.dirname, "documents")
        self.assertIsNone(req.summary)

    def test_accepts_none_summary(self):
        req = FolderUpdateRequest(
            dirname="documents",
            summary=None,
        )

        self.assertEqual(req.dirname, "documents")
        self.assertIsNone(req.summary)

    def test_strips_whitespace(self):
        req = FolderUpdateRequest(
            dirname="  documents  ",
            summary="  Folder summary.  ",
        )

        self.assertEqual(req.dirname, "documents")
        self.assertEqual(req.summary, "Folder summary.")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FolderUpdateRequest(
                dirname="documents",
                summary="Folder summary.",
                other=1,
            )

    def test_dirname_required(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(
                summary="Folder summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "missing")

    def test_dirname_too_short_after_stripping(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(
                dirname="   ",
                summary="Folder summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "string_too_short")

    def test_dirname_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(
                dirname=("a" * 256),
                summary="Folder summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(
                dirname="documents",
                summary=("a" * 4097),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("summary",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_empty_string_normalized_to_none(self):
        req = FolderUpdateRequest(
            dirname="documents",
            summary="",
        )

        self.assertIsNone(req.summary)

    def test_summary_whitespace_only_normalized_to_none(self):
        req = FolderUpdateRequest(
            dirname="documents",
            summary="   ",
        )

        self.assertIsNone(req.summary)

    def test_accepts_dirname_with_extension(self):
        req = FolderUpdateRequest(
            dirname="documents.txt",
            summary=None,
        )

        self.assertEqual(req.dirname, "documents.txt")

    def test_accepts_dirname_with_inner_dots(self):
        req = FolderUpdateRequest(
            dirname="archive.tar.gz",
            summary=None,
        )

        self.assertEqual(req.dirname, "archive.tar.gz")

    def test_accepts_dirname_with_leading_dot_when_not_dot_segment(self):
        req = FolderUpdateRequest(
            dirname=".config",
            summary=None,
        )

        self.assertEqual(req.dirname, ".config")

    def test_rejects_dot_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(dirname=".", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_double_dot_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(dirname="..", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_forward_slash_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(dirname="foo/bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_backslash_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(dirname="foo\\bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_null_byte_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(dirname="foo\x00bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_control_character_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderUpdateRequest(dirname="foo\nbar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")
