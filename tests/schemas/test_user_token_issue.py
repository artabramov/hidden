# tests/schemas/test_user_token_issue.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.user_token_issue import (
    TokenIssueRequest,
    TokenIssueResponse,
)


def _session_uuid(length: int = 36) -> str:
    """Valid mfa_session_uuid length for tests (20 <= n <= 80)."""
    assert 20 <= length <= 80
    return "u" * length


class TestTokenIssueRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = TokenIssueRequest(
            mfa_session_uuid=_session_uuid(36),
            totp="123456",
        )

        self.assertEqual(len(req.mfa_session_uuid), 36)
        self.assertEqual(req.totp, "123456")

    def test_strips_whitespace(self):
        inner = _session_uuid(20)
        req = TokenIssueRequest(
            mfa_session_uuid=f"  {inner}  ",
            totp="  123456  ",
        )

        self.assertEqual(req.mfa_session_uuid, inner)
        self.assertEqual(req.totp, "123456")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            TokenIssueRequest(
                mfa_session_uuid=_session_uuid(20),
                totp="123456",
                other=1,
            )

    def test_mfa_session_uuid_required(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                totp="123456",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("mfa_session_uuid",))
        self.assertEqual(error["type"], "missing")

    def test_totp_required(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid=_session_uuid(20),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("totp",))
        self.assertEqual(error["type"], "missing")

    def test_mfa_session_uuid_rejects_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid="t" * 19,
                totp="123456",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("mfa_session_uuid",))
        self.assertEqual(error["type"], "string_too_short")

    def test_mfa_session_uuid_rejects_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid="t" * 81,
                totp="123456",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("mfa_session_uuid",))
        self.assertEqual(error["type"], "string_too_long")

    def test_accepts_mfa_session_uuid_at_min_length(self):
        value = _session_uuid(20)
        req = TokenIssueRequest(
            mfa_session_uuid=value,
            totp="654321",
        )

        self.assertEqual(req.mfa_session_uuid, value)
        self.assertEqual(len(req.mfa_session_uuid), 20)

    def test_accepts_mfa_session_uuid_at_max_length(self):
        value = _session_uuid(80)
        req = TokenIssueRequest(
            mfa_session_uuid=value,
            totp="000000",
        )

        self.assertEqual(req.mfa_session_uuid, value)
        self.assertEqual(len(req.mfa_session_uuid), 80)

    def test_totp_rejects_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid=_session_uuid(20),
                totp="12345",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("totp",))
        self.assertEqual(error["type"], "string_too_short")

    def test_totp_rejects_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid=_session_uuid(20),
                totp="1234567",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("totp",))
        self.assertEqual(error["type"], "string_too_long")

    def test_totp_rejects_non_digits(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid=_session_uuid(20),
                totp="ABCDEF",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("totp",))
        self.assertEqual(error["type"], "string_pattern_mismatch")

    def test_totp_rejects_mixed_alphanumeric(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid=_session_uuid(20),
                totp="12345a",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("totp",))
        self.assertEqual(error["type"], "string_pattern_mismatch")

    def test_totp_rejects_inner_space_after_strip(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueRequest(
                mfa_session_uuid=_session_uuid(20),
                totp="12 456",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("totp",))
        self.assertEqual(error["type"], "string_pattern_mismatch")


class TestTokenIssueResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = TokenIssueResponse(
            user_id=1,
            auth_token="token-value",
        )

        self.assertEqual(resp.user_id, 1)
        self.assertEqual(resp.auth_token, "token-value")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            TokenIssueResponse(
                user_id=1,
                auth_token="token-value",
                other=1,
            )

    def test_user_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueResponse(
                auth_token="token-value",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("user_id",))
        self.assertEqual(error["type"], "missing")

    def test_auth_token_required(self):
        with self.assertRaises(ValidationError) as cm:
            TokenIssueResponse(
                user_id=1,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("auth_token",))
        self.assertEqual(error["type"], "missing")
