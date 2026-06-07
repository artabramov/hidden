# tests/schemas/test_user_role_change.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.user_role_change import UserRoleChangeRequest


class TestUserRoleChangeRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = UserRoleChangeRequest(
            role="admin",
            is_active=True,
        )

        self.assertEqual(req.role, "admin")
        self.assertTrue(req.is_active)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserRoleChangeRequest(
                role="admin",
                is_active=True,
                other=1,
            )

    def test_role_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRoleChangeRequest(
                is_active=True,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("role",))
        self.assertEqual(error["type"], "missing")

    def test_is_active_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRoleChangeRequest(
                role="admin",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("is_active",))
        self.assertEqual(error["type"], "missing")

    def test_rejects_invalid_role(self):
        with self.assertRaises(ValidationError) as cm:
            UserRoleChangeRequest(
                role="owner",
                is_active=True,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("role",))
        self.assertEqual(error["type"], "enum")

    def test_accepts_false_is_active(self):
        req = UserRoleChangeRequest(
            role="reader",
            is_active=False,
        )

        self.assertEqual(req.role, "reader")
        self.assertFalse(req.is_active)
