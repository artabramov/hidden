# tests/schemas/test_folder_list.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.folder_list import (
    FolderListRequest,
    FolderListResponse,
)


class TestFolderListRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = FolderListRequest(
            parent_id__eq=7,
            order_by="dirname",
            order="asc",
        )

        self.assertEqual(req.parent_id__eq, 7)
        self.assertEqual(req.order_by, "dirname")
        self.assertEqual(req.order, "asc")

    def test_uses_defaults(self):
        req = FolderListRequest()

        self.assertIsNone(req.parent_id__eq)
        self.assertEqual(req.order_by, "dirname")
        self.assertEqual(req.order, "asc")

    def test_parent_id_eq_explicit_none(self):
        req = FolderListRequest(parent_id__eq=None)

        self.assertIsNone(req.parent_id__eq)

    def test_parent_id_eq_rejects_non_positive_value(self):
        with self.assertRaises(ValidationError) as cm:
            FolderListRequest(parent_id__eq=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("parent_id__eq",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FolderListRequest(other=1)

    def test_order_by_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as cm:
            FolderListRequest(order_by="name")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("order_by",))
        self.assertEqual(error["type"], "literal_error")

    def test_order_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as cm:
            FolderListRequest(order="rand")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("order",))
        self.assertEqual(error["type"], "literal_error")


class TestFolderListResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = FolderListResponse(
            folders=[
                {
                    "folder_id": 1,
                    "parent_id": None,
                    "created_by": {"id": 10, "display_name": "List Creator"},
                    "created_at": 100,
                    "updated_at": 200,
                    "updated_by": {"id": 20, "display_name": "List Editor"},
                    "dirname": "documents",
                    "is_write_protected": False,
                    "is_write_protected_recursive": False,
                    "children_count": 3,
                    "files_count": 5,
                    "summary": "Folder summary.",
                }
            ],
            folders_count=1,
        )

        self.assertEqual(len(resp.folders), 1)
        self.assertEqual(resp.folders_count, 1)
        self.assertEqual(resp.folders[0].folder_id, 1)
        self.assertEqual(resp.folders[0].created_by.user_id, 10)
        self.assertEqual(
            resp.folders[0].created_by.display_name,
            "List Creator"
        )
        self.assertEqual(resp.folders[0].updated_by.user_id, 20)
        self.assertEqual(resp.folders[0].dirname, "documents")
        self.assertFalse(resp.folders[0].is_write_protected_recursive)
        self.assertEqual(resp.folders[0].children_count, 3)
        self.assertEqual(resp.folders[0].files_count, 5)

    def test_accepts_empty_folders(self):
        resp = FolderListResponse(
            folders=[],
            folders_count=0,
        )

        self.assertEqual(resp.folders, [])
        self.assertEqual(resp.folders_count, 0)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FolderListResponse(
                folders=[],
                folders_count=0,
                other=1,
            )

    def test_folders_required(self):
        with self.assertRaises(ValidationError) as cm:
            FolderListResponse(folders_count=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folders",))
        self.assertEqual(error["type"], "missing")

    def test_folders_count_required(self):
        with self.assertRaises(ValidationError) as cm:
            FolderListResponse(folders=[])

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folders_count",))
        self.assertEqual(error["type"], "missing")

    def test_folders_count_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            FolderListResponse(
                folders=[],
                folders_count=-1,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folders_count",))
        self.assertEqual(error["type"], "greater_than_equal")
