# tests/schemas/test_user_totp_recover.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.user_totp_recover import (
    UserTotpRecoverRequest,
    UserTotpRecoverResponse,
)


class TestUserTotpRecoverRequest(unittest.TestCase):
    def test_accepts_valid_payload(self):
        req = UserTotpRecoverRequest(
            mfa_session_uuid="session-" + "a" * 25,
            recovery_code="ABCD-ABCD-ABCD-ABCD-ABCD-ABCD",
        )

        self.assertTrue(req.mfa_session_uuid.startswith("session-"))
        self.assertEqual(
            req.recovery_code,
            "ABCD-ABCD-ABCD-ABCD-ABCD-ABCD",
        )

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserTotpRecoverRequest(
                mfa_session_uuid="session-" + "a" * 25,
                recovery_code="ABCD-ABCD-ABCD-ABCD-ABCD-ABCD",
                x=1,
            )

    def test_recovery_code_strips_surrounding_whitespace(self):
        canon = "ABCD-ABCD-ABCD-ABCD-ABCD-ABCD"
        req = UserTotpRecoverRequest(
            mfa_session_uuid="session-" + "a" * 25,
            recovery_code="  " + canon + "  ",
        )
        self.assertEqual(req.recovery_code, canon)


class TestUserTotpRecoverResponse(unittest.TestCase):
    def test_accepts_valid_payload(self):
        resp = UserTotpRecoverResponse(
            user_id=3,
            totp_secret="SECRET",
        )

        self.assertEqual(resp.user_id, 3)
        self.assertEqual(resp.totp_secret, "SECRET")
