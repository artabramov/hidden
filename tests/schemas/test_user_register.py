# tests/schemas/test_user_register.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.user_register import (
    UserRegisterRequest,
    UserRegisterResponse,
)


class TestUserRegisterRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = UserRegisterRequest(
            username="testuser",
            password="StrongPass9",
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(req.username, "testuser")
        self.assertEqual(req.password, "StrongPass9")
        self.assertEqual(req.display_name, "Test User")
        self.assertEqual(req.summary, "Profile summary.")

    def test_accepts_none_summary(self):
        req = UserRegisterRequest(
            username="testuser",
            password="StrongPass9",
            display_name="Test User",
            summary=None,
        )

        self.assertIsNone(req.summary)

    def test_strips_whitespace(self):
        req = UserRegisterRequest(
            username="  testuser  ",
            password="  StrongPass9  ",
            display_name="  Test User  ",
            summary="  Profile summary.  ",
        )

        self.assertEqual(req.username, "testuser")
        self.assertEqual(req.password, "  StrongPass9  ")
        self.assertEqual(req.display_name, "Test User")
        self.assertEqual(req.summary, "Profile summary.")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="testuser",
                password="StrongPass9",
                display_name="Test User",
                summary="Profile summary.",
                other=1,
            )

    def test_username_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                password="StrongPass9",
                display_name="Test User",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "missing")

    def test_password_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="testuser",
                display_name="Test User",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("password",))
        self.assertEqual(error["type"], "missing")

    def test_display_name_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="testuser",
                password="StrongPass9",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("display_name",))
        self.assertEqual(error["type"], "missing")

    def test_username_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="abc",
                password="StrongPass9",
                display_name="Test User",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "string_too_short")

    def test_username_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username=("a" * 41),
                password="StrongPass9",
                display_name="Test User",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "string_too_long")

    def test_username_accepts_hyphen(self):
        req = UserRegisterRequest(
            username="test-user",
            password="StrongPass9",
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(req.username, "test-user")

    def test_username_accepts_underscore(self):
        req = UserRegisterRequest(
            username="test_user",
            password="StrongPass9",
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(req.username, "test_user")

    def test_username_rejects_invalid_characters(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="test.user",
                password="StrongPass9",
                display_name="Test User",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "value_not_latin_extended")

    def test_username_rejects_whitespace_inside(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="test user",
                password="StrongPass9",
                display_name="Test User",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "value_not_latin_extended")

    def test_username_is_stripped_and_lowercased(self):
        req = UserRegisterRequest(
            username="  TestUser  ",
            password="StrongPass9",
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(req.username, "testuser")

    def test_username_is_normalized_to_lowercase(self):
        req = UserRegisterRequest(
            username="TestUser",
            password="StrongPass9",
            display_name="Test User",
            summary="Profile summary.",
        )

        self.assertEqual(req.username, "testuser")

    def test_password_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="testuser",
                password="Aa1aa1a",
                display_name="Test User",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("password",))
        self.assertEqual(error["type"], "string_too_short")

    def test_display_name_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="testuser",
                password="StrongPass9",
                display_name="abc",
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("display_name",))
        self.assertEqual(error["type"], "string_too_short")

    def test_display_name_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="testuser",
                password="StrongPass9",
                display_name=("a" * 41),
                summary="Profile summary.",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("display_name",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterRequest(
                username="testuser",
                password="StrongPass9",
                display_name="Test User",
                summary=("a" * 4097),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("summary",))
        self.assertEqual(error["type"], "string_too_long")

    def test_summary_empty_string_normalized_to_none(self):
        req = UserRegisterRequest(
            username="testuser",
            password="StrongPass9",
            display_name="Test User",
            summary="",
        )

        self.assertIsNone(req.summary)

    def test_summary_whitespace_only_normalized_to_none(self):
        req = UserRegisterRequest(
            username="testuser",
            password="StrongPass9",
            display_name="Test User",
            summary="   ",
        )

        self.assertIsNone(req.summary)


class TestUserRegisterResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = UserRegisterResponse(
            user_id=1,
            totp_secret="SECRET123",
            recovery_code="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
        )

        self.assertEqual(resp.user_id, 1)
        self.assertEqual(resp.totp_secret, "SECRET123")
        self.assertEqual(resp.recovery_code, "WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserRegisterResponse(
                user_id=1,
                totp_secret="SECRET123",
                recovery_code="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
                other=1,
            )

    def test_user_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterResponse(
                totp_secret="SECRET123",
                recovery_code="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("user_id",))
        self.assertEqual(error["type"], "missing")

    def test_totp_secret_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterResponse(
                user_id=1,
                recovery_code="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("totp_secret",))
        self.assertEqual(error["type"], "missing")

    def test_recovery_code_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRegisterResponse(
                user_id=1,
                totp_secret="SECRET123",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("recovery_code",))
        self.assertEqual(error["type"], "missing")
