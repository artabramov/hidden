# tests/schemas/test_user_update.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.user_update import UserUpdateRequest


class TestUserUpdateRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = UserUpdateRequest(
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(req.display_name, "Test User")
        self.assertEqual(req.summary, "Profile summary.")

    def test_accepts_none_summary(self):
        req = UserUpdateRequest(
            display_name="Test User",
            summary=None,
        )

        self.assertEqual(req.display_name, "Test User")
        self.assertIsNone(req.summary)

    def test_strips_whitespace(self):
        req = UserUpdateRequest(
            display_name="  Test User  ",
            summary="  Profile summary.  ",
        )

        self.assertEqual(req.display_name, "Test User")
        self.assertEqual(req.summary, "Profile summary.")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserUpdateRequest(
                display_name="Test User",
                summary="Profile summary.",
                other=1,
            )

    def test_display_name_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserUpdateRequest(
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("display_name",))
        self.assertEqual(error["type"], "missing")

    def test_display_name_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserUpdateRequest(
                display_name="abc",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("display_name",))
        self.assertEqual(error["type"], "string_too_short")

    def test_display_name_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            UserUpdateRequest(
                display_name=("a" * 41),
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("display_name",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            UserUpdateRequest(
                display_name="Test User",
                summary=("a" * 4097),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("summary",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_empty_string_normalized_to_none(self):
        req = UserUpdateRequest(
            display_name="Test User",
            summary="",
        )

        self.assertIsNone(req.summary)

    def test_summary_whitespace_only_normalized_to_none(self):
        req = UserUpdateRequest(
            display_name="Test User",
            summary="   ",
        )

        self.assertIsNone(req.summary)
