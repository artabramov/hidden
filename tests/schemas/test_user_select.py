# tests/schemas/test_user_select.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.user_select import UserSelectResponse


class TestUserSelectResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = UserSelectResponse(
            user_id=1,
            created_at=100,
            last_authenticated_at=200,
            role="admin",
            is_active=True,
            username="testuser",
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(resp.user_id, 1)
        self.assertEqual(resp.created_at, 100)
        self.assertEqual(resp.last_authenticated_at, 200)
        self.assertEqual(resp.role, "admin")
        self.assertTrue(resp.is_active)
        self.assertEqual(resp.username, "testuser")
        self.assertEqual(resp.display_name, "Test User")
        self.assertEqual(resp.summary, "Profile summary.")

    def test_accepts_none_optional_fields(self):
        resp = UserSelectResponse(
            user_id=1,
            created_at=100,
            last_authenticated_at=None,
            role="reader",
            is_active=False,
            username="testuser",
            display_name="Test User",
            summary=None,
        )

        self.assertIsNone(resp.last_authenticated_at)
        self.assertIsNone(resp.summary)

    def test_accepts_validation_alias_id(self):
        resp = UserSelectResponse(
            id=1,
            created_at=100,
            last_authenticated_at=200,
            role="admin",
            is_active=True,
            username="testuser",
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(resp.user_id, 1)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserSelectResponse(
                user_id=1,
                created_at=100,
                last_authenticated_at=200,
                role="admin",
                is_active=True,
                username="testuser",
                display_name="Test User",
                summary="Profile summary.",
                other=1,
            )

    def test_required_fields(self):
        required_fields = [
            "id",
            "created_at",
            "role",
            "is_active",
            "username",
            "display_name",
        ]

        for field in required_fields:
            data = {
                "id": 1,
                "created_at": 100,
                "last_authenticated_at": 200,
                "role": "admin",
                "is_active": True,
                "username": "testuser",
                "display_name": "Test User",
                "summary": "Profile summary.",
            }
            data.pop(field)

            with self.assertRaises(ValidationError) as cm:
                UserSelectResponse(**data)

            error = cm.exception.errors()[0]
            self.assertEqual(error["loc"], (field,))
            self.assertEqual(error["type"], "missing")

    def test_accepts_object_attributes(self):
        class Obj:
            id = 7
            created_at = 100
            last_authenticated_at = None
            role = "writer"
            is_active = True
            username = "user"
            display_name = "User Name"
            summary = None

        resp = UserSelectResponse.model_validate(Obj())

        self.assertEqual(resp.user_id, 7)
        self.assertEqual(resp.role, "writer")
