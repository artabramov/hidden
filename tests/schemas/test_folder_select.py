# tests/schemas/test_folder_select.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace
from pydantic import ValidationError

from app.schemas.folder_select import (
    FolderSelectResponse,
    FolderSelectUserResponse,
    build_folder_response,
)


class TestFolderSelectUserResponse(unittest.TestCase):

    def test_accepts_user_id_and_display_name(self):
        resp = FolderSelectUserResponse(user_id=5, display_name="Alice")

        self.assertEqual(resp.user_id, 5)
        self.assertEqual(resp.display_name, "Alice")

    def test_accepts_validation_alias_id(self):
        resp = FolderSelectUserResponse(id=9, display_name="Bob")

        self.assertEqual(resp.user_id, 9)
        self.assertEqual(resp.display_name, "Bob")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FolderSelectUserResponse(user_id=1, display_name="x", extra=1)


class TestFolderSelectResponse(unittest.TestCase):

    def _created_by(self):
        return FolderSelectUserResponse(user_id=99, display_name="Creator")

    def test_accepts_valid_payload(self):
        resp = FolderSelectResponse(
            folder_id=1,
            parent_id=2,
            created_by=self._created_by(),
            created_at=100,
            updated_at=200,
            updated_by=FolderSelectUserResponse(
                user_id=88,
                display_name="Editor",
            ),
            dirname="documents",
            is_write_protected=False,
            is_write_protected_recursive=True,
            children_count=3,
            files_count=4,
            summary="Folder summary.",
        )

        self.assertEqual(resp.folder_id, 1)
        self.assertEqual(resp.parent_id, 2)
        self.assertEqual(resp.created_by.user_id, 99)
        self.assertEqual(resp.created_by.display_name, "Creator")
        self.assertEqual(resp.created_at, 100)
        self.assertEqual(resp.updated_by.user_id, 88)
        self.assertEqual(resp.updated_by.display_name, "Editor")
        self.assertEqual(resp.updated_at, 200)
        self.assertEqual(resp.dirname, "documents")
        self.assertFalse(resp.is_write_protected)
        self.assertTrue(resp.is_write_protected_recursive)
        self.assertEqual(resp.children_count, 3)
        self.assertEqual(resp.files_count, 4)
        self.assertEqual(resp.summary, "Folder summary.")

    def test_accepts_none_optional_fields(self):
        resp = FolderSelectResponse(
            folder_id=1,
            parent_id=None,
            created_by=self._created_by(),
            created_at=100,
            updated_at=None,
            updated_by=None,
            dirname="documents",
            is_write_protected=True,
            is_write_protected_recursive=True,
            children_count=0,
            files_count=0,
            summary=None,
        )

        self.assertIsNone(resp.parent_id)
        self.assertIsNone(resp.updated_at)
        self.assertIsNone(resp.updated_by)
        self.assertTrue(resp.is_write_protected_recursive)
        self.assertEqual(resp.children_count, 0)
        self.assertEqual(resp.files_count, 0)
        self.assertIsNone(resp.summary)

    def test_accepts_validation_alias_id(self):
        resp = FolderSelectResponse(
            id=1,
            parent_id=None,
            created_by={"id": 42, "display_name": "Pat"},
            created_at=100,
            updated_at=None,
            updated_by=None,
            dirname="documents",
            is_write_protected=False,
            is_write_protected_recursive=False,
            children_count=0,
            files_count=0,
            summary=None,
        )

        self.assertEqual(resp.folder_id, 1)
        self.assertEqual(resp.created_by.user_id, 42)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FolderSelectResponse(
                folder_id=1,
                parent_id=None,
                created_by=self._created_by(),
                created_at=100,
                updated_at=None,
                updated_by=None,
                dirname="documents",
                is_write_protected=False,
                is_write_protected_recursive=False,
                children_count=0,
                files_count=0,
                summary=None,
                other=1,
            )

    def test_required_fields(self):
        required_fields = [
            "id",
            "created_by",
            "created_at",
            "dirname",
            "is_write_protected",
            "is_write_protected_recursive",
            "children_count",
            "files_count",
        ]

        for field in required_fields:
            data = {
                "id": 1,
                "parent_id": None,
                "created_by": {"id": 7, "display_name": "Owner"},
                "created_at": 100,
                "updated_at": None,
                "updated_by": None,
                "dirname": "documents",
                "is_write_protected": False,
                "is_write_protected_recursive": False,
                "children_count": 0,
                "files_count": 0,
                "summary": None,
            }
            data.pop(field)

            with self.assertRaises(ValidationError) as cm:
                FolderSelectResponse(**data)

            error = cm.exception.errors()[0]
            self.assertEqual(error["loc"], (field,))
            self.assertEqual(error["type"], "missing")

    def test_children_count_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            FolderSelectResponse(
                folder_id=1,
                parent_id=None,
                created_by=self._created_by(),
                created_at=100,
                updated_at=None,
                updated_by=None,
                dirname="documents",
                is_write_protected=False,
                is_write_protected_recursive=False,
                children_count=-1,
                files_count=0,
                summary=None,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("children_count",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_files_count_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            FolderSelectResponse(
                folder_id=1,
                parent_id=None,
                created_by=self._created_by(),
                created_at=100,
                updated_at=None,
                updated_by=None,
                dirname="documents",
                is_write_protected=False,
                is_write_protected_recursive=False,
                children_count=0,
                files_count=-1,
                summary=None,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("files_count",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_accepts_object_attributes(self):
        class Obj:
            id = 7
            parent_id = None
            created_at = 100
            updated_at = None
            updated_by = None
            dirname = "documents"
            is_write_protected = True
            is_write_protected_recursive = True
            children_count = 4
            files_count = 6
            summary = None
            created_by = SimpleNamespace(id=3, display_name="Sam")

        resp = FolderSelectResponse.model_validate(Obj())

        self.assertEqual(resp.folder_id, 7)
        self.assertIsNone(resp.parent_id)
        self.assertEqual(resp.created_by.user_id, 3)
        self.assertEqual(resp.created_by.display_name, "Sam")
        self.assertEqual(resp.dirname, "documents")
        self.assertTrue(resp.is_write_protected)
        self.assertTrue(resp.is_write_protected_recursive)
        self.assertEqual(resp.children_count, 4)
        self.assertEqual(resp.files_count, 6)


class TestBuildFolderResponse(unittest.TestCase):

    def _folder_with_users(
        self,
        *,
        folder_id,
        parent_id,
        dirname,
        is_write_protected,
        summary,
        updated_at=None,
        updater=None,
        children_count=0,
        files_count=0,
    ):
        return SimpleNamespace(
            id=folder_id,
            parent_id=parent_id,
            created_at=100,
            updated_at=updated_at,
            dirname=dirname,
            is_write_protected=is_write_protected,
            children_count=children_count,
            files_count=files_count,
            summary=summary,
            folder_created_by_user=SimpleNamespace(
                id=10,
                display_name="Creator User",
            ),
            folder_updated_by_user=updater,
        )

    def test_builds_response_without_recursive_protection(self):
        folder = self._folder_with_users(
            folder_id=1,
            parent_id=None,
            dirname="documents",
            is_write_protected=False,
            summary=None,
        )

        resp = build_folder_response(
            folder,
            is_write_protected_recursive=False,
        )

        self.assertIsInstance(resp, FolderSelectResponse)
        self.assertEqual(resp.folder_id, 1)
        self.assertEqual(resp.created_by.user_id, 10)
        self.assertEqual(resp.created_by.display_name, "Creator User")
        self.assertIsNone(resp.updated_by)
        self.assertFalse(resp.is_write_protected)
        self.assertFalse(resp.is_write_protected_recursive)
        self.assertEqual(resp.children_count, 0)
        self.assertEqual(resp.files_count, 0)

    def test_builds_response_with_inherited_recursive_protection(self):
        folder = self._folder_with_users(
            folder_id=2,
            parent_id=1,
            dirname="child",
            is_write_protected=False,
            summary=None,
            updater=SimpleNamespace(id=20, display_name="Editor User"),
            updated_at=200,
        )

        resp = build_folder_response(
            folder,
            is_write_protected_recursive=True,
        )

        self.assertFalse(resp.is_write_protected)
        self.assertTrue(resp.is_write_protected_recursive)
        self.assertIsNotNone(resp.updated_by)
        self.assertEqual(resp.updated_by.user_id, 20)
        self.assertEqual(resp.updated_by.display_name, "Editor User")
        self.assertEqual(resp.updated_at, 200)

    def test_builds_response_with_own_protection_only(self):
        folder = self._folder_with_users(
            folder_id=3,
            parent_id=None,
            dirname="private",
            is_write_protected=True,
            summary=None,
        )

        resp = build_folder_response(
            folder,
            is_write_protected_recursive=False,
        )

        self.assertTrue(resp.is_write_protected)
        self.assertFalse(resp.is_write_protected_recursive)

    def test_builds_response_propagates_child_and_file_counters(self):
        folder = self._folder_with_users(
            folder_id=4,
            parent_id=None,
            dirname="counted",
            is_write_protected=False,
            summary=None,
            children_count=7,
            files_count=11,
        )

        resp = build_folder_response(
            folder,
            is_write_protected_recursive=False,
        )

        self.assertEqual(resp.children_count, 7)
        self.assertEqual(resp.files_count, 11)
