# tests/schemas/folder_create.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.schemas.folder_create import (
    FolderCreateRequest,
    FolderCreateResponse,
)


class TestFolderCreateRequest(unittest.TestCase):

    def test_accepts_valid_payload_with_parent(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname="documents",
            summary="Folder summary.",
        )

        self.assertEqual(req.parent_id, 1)
        self.assertEqual(req.dirname, "documents")
        self.assertEqual(req.summary, "Folder summary.")

    def test_accepts_valid_payload_in_root(self):
        req = FolderCreateRequest(
            parent_id=None,
            dirname="documents",
            summary="Folder summary.",
        )

        self.assertIsNone(req.parent_id)
        self.assertEqual(req.dirname, "documents")
        self.assertEqual(req.summary, "Folder summary.")

    def test_accepts_none_summary(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname="documents",
            summary=None,
        )

        self.assertIsNone(req.summary)

    def test_strips_whitespace(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname="  documents  ",
            summary="  Folder summary.  ",
        )

        self.assertEqual(req.parent_id, 1)
        self.assertEqual(req.dirname, "documents")
        self.assertEqual(req.summary, "Folder summary.")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FolderCreateRequest(
                parent_id=1,
                dirname="documents",
                summary="Folder summary.",
                other=1,
            )

    def test_dirname_required(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(
                parent_id=1,
                summary="Folder summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "missing")

    def test_parent_id_may_be_omitted(self):
        req = FolderCreateRequest(
            dirname="documents",
            summary="Folder summary.",
        )

        self.assertIsNone(req.parent_id)
        self.assertEqual(req.dirname, "documents")
        self.assertEqual(req.summary, "Folder summary.")

    def test_parent_id_must_be_positive_if_provided(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(
                parent_id=0,
                dirname="documents",
                summary="Folder summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("parent_id",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_dirname_too_short_after_stripping(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(
                parent_id=1,
                dirname="   ",
                summary="Folder summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "string_too_short")

    def test_dirname_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(
                parent_id=1,
                dirname=("a" * 256),
                summary="Folder summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(
                parent_id=1,
                dirname="documents",
                summary=("a" * 4097),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("summary",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_empty_string_normalized_to_none(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname="documents",
            summary="",
        )

        self.assertIsNone(req.summary)

    def test_summary_whitespace_only_normalized_to_none(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname="documents",
            summary="   ",
        )

        self.assertIsNone(req.summary)

    def test_accepts_dirname_with_extension(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname="documents.txt",
            summary=None,
        )

        self.assertEqual(req.dirname, "documents.txt")

    def test_accepts_dirname_with_inner_dots(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname="archive.tar.gz",
            summary=None,
        )

        self.assertEqual(req.dirname, "archive.tar.gz")

    def test_accepts_dirname_with_leading_dot_when_not_dot_segment(self):
        req = FolderCreateRequest(
            parent_id=1,
            dirname=".config",
            summary=None,
        )

        self.assertEqual(req.dirname, ".config")

    def test_rejects_dot_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(parent_id=1, dirname=".", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_double_dot_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(parent_id=1, dirname="..", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_forward_slash_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(parent_id=1, dirname="foo/bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_backslash_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(parent_id=1, dirname="foo\\bar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_null_byte_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(
                parent_id=1, dirname="foo\x00bar", summary=None
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")

    def test_rejects_control_character_in_dirname(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateRequest(parent_id=1, dirname="foo\nbar", summary=None)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "value_not_path_segment")


class TestFolderCreateResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FolderCreateResponse(
            id=1,
        )

        self.assertEqual(resp.folder_id, 1)

    def test_accepts_object_from_attributes(self):
        folder = MagicMock()
        folder.id = 1

        resp = FolderCreateResponse.model_validate(folder)

        self.assertEqual(resp.folder_id, 1)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FolderCreateResponse(
                id=1,
                other=1,
            )

    def test_folder_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            FolderCreateResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")
