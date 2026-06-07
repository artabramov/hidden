# tests/schemas/test_user_password_change.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.user_password_change import UserPasswordChangeRequest


class TestUserPasswordChangeRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = UserPasswordChangeRequest(
            current_password="CurrentPass9",
            changed_password="ChangedPass9",
        )

        self.assertEqual(req.current_password, "CurrentPass9")
        self.assertEqual(req.changed_password, "ChangedPass9")

    def test_not_strip_whitespace(self):
        req = UserPasswordChangeRequest(
            current_password="  CurrentPass9  ",
            changed_password="  ChangedPass9  ",
        )

        self.assertEqual(req.current_password, "  CurrentPass9  ")
        self.assertEqual(req.changed_password, "  ChangedPass9  ")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserPasswordChangeRequest(
                current_password="CurrentPass9",
                changed_password="ChangedPass9",
                other=1,
            )

    def test_current_password_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserPasswordChangeRequest(
                changed_password="ChangedPass9",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("current_password",))
        self.assertEqual(error["type"], "missing")

    def test_changed_password_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserPasswordChangeRequest(
                current_password="CurrentPass9",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("changed_password",))
        self.assertEqual(error["type"], "missing")

    def test_current_password_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserPasswordChangeRequest(
                current_password="Aa1aa1a",
                changed_password="ChangedPass9",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("current_password",))
        self.assertEqual(error["type"], "string_too_short")

    def test_changed_password_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserPasswordChangeRequest(
                current_password="CurrentPass9",
                changed_password="Aa1aa1a",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("changed_password",))
        self.assertEqual(error["type"], "string_too_short")
