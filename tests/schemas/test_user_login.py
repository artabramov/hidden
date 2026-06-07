# tests/schemas/test_user_login.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.user_login import UserLoginRequest, UserLoginResponse


class TestUserLoginRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = UserLoginRequest(
            username="testuser",
            password="StrongPass9",
        )

        self.assertEqual(req.username, "testuser")
        self.assertEqual(req.password, "StrongPass9")

    def test_strips_whitespace(self):
        req = UserLoginRequest(
            username="  testuser  ",
            password="  StrongPass9  ",
        )

        self.assertEqual(req.username, "testuser")
        self.assertEqual(req.password, "  StrongPass9  ")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserLoginRequest(
                username="testuser",
                password="StrongPass9",
                other=1,
            )

    def test_username_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginRequest(
                password="StrongPass9",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "missing")

    def test_password_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginRequest(
                username="testuser",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("password",))
        self.assertEqual(error["type"], "missing")

    def test_username_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginRequest(
                username="abc",
                password="StrongPass9",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "string_too_short")

    def test_username_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginRequest(
                username=("a" * 41),
                password="StrongPass9",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("username",))
        self.assertEqual(error["type"], "string_too_long")

    def test_username_is_normalized_to_lowercase(self):
        req = UserLoginRequest(
            username="TestUser",
            password="StrongPass9",
        )

        self.assertEqual(req.username, "testuser")

    def test_username_is_stripped(self):
        req = UserLoginRequest(
            username="  testuser  ",
            password="StrongPass9",
        )

        self.assertEqual(req.username, "testuser")

    def test_username_is_stripped_and_lowercased(self):
        req = UserLoginRequest(
            username="  TestUser  ",
            password="StrongPass9",
        )

        self.assertEqual(req.username, "testuser")

    def test_password_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginRequest(
                username="testuser",
                password="Aa1aa1a",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("password",))
        self.assertEqual(error["type"], "string_too_short")

    def test_preserves_password_leading_and_trailing_whitespace(self):
        req = UserLoginRequest(
            username="testuser",
            password="  StrongPass9  ",
        )

        self.assertEqual(req.username, "testuser")
        self.assertEqual(req.password, "  StrongPass9  ")

    def test_strips_username_but_not_password(self):
        req = UserLoginRequest(
            username="  testuser  ",
            password="  StrongPass9  ",
        )

        self.assertEqual(req.username, "testuser")
        self.assertEqual(req.password, "  StrongPass9  ")

    def test_password_with_only_edge_whitespace_counts_in_length(self):
        req = UserLoginRequest(
            username="testuser",
            password="       a",
        )

        self.assertEqual(req.password, "       a")
        self.assertEqual(len(req.password), 8)

    def test_password_whitespace_only_is_valid_when_length_is_enough(self):
        req = UserLoginRequest(
            username="testuser",
            password="        ",
        )

        self.assertEqual(req.password, "        ")


class TestUserLoginResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = UserLoginResponse(
            mfa_session_uuid="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )

        self.assertEqual(
            resp.mfa_session_uuid,
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )

    def test_accepts_mfa_session_uuid_at_min_length(self):
        value = "z" * 20
        resp = UserLoginResponse(mfa_session_uuid=value)

        self.assertEqual(resp.mfa_session_uuid, value)
        self.assertEqual(len(resp.mfa_session_uuid), 20)

    def test_accepts_mfa_session_uuid_at_max_length(self):
        value = "x" * 80
        resp = UserLoginResponse(mfa_session_uuid=value)

        self.assertEqual(resp.mfa_session_uuid, value)
        self.assertEqual(len(resp.mfa_session_uuid), 80)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserLoginResponse(
                mfa_session_uuid="a" * 20,
                other=1,
            )

    def test_mfa_session_uuid_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("mfa_session_uuid",))
        self.assertEqual(error["type"], "missing")

    def test_mfa_session_uuid_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginResponse(mfa_session_uuid=("b" * 19))

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("mfa_session_uuid",))
        self.assertEqual(error["type"], "string_too_short")

    def test_mfa_session_uuid_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            UserLoginResponse(mfa_session_uuid=("y" * 81))

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("mfa_session_uuid",))
        self.assertEqual(error["type"], "string_too_long")
