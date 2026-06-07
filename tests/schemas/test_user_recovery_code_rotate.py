# tests/schemas/test_user_recovery_code_rotate.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.user_recovery_code_rotate import (
    UserRecoveryCodeRotateRequest,
    UserRecoveryCodeRotateResponse,
)

_CANON = "ABCD-ABCD-ABCD-ABCD-ABCD-ABCD"


class TestUserRecoveryCodeRotateRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = UserRecoveryCodeRotateRequest(
            recovery_code=_CANON,
        )

        self.assertEqual(req.recovery_code, _CANON)

    def test_recovery_code_strips_surrounding_whitespace(self):
        req = UserRecoveryCodeRotateRequest(
            recovery_code="  " + _CANON + "  ",
        )

        self.assertEqual(req.recovery_code, _CANON)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserRecoveryCodeRotateRequest(
                recovery_code=_CANON,
                other=1,
            )

    def test_recovery_code_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserRecoveryCodeRotateRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("recovery_code",))
        self.assertEqual(error["type"], "missing")

    def test_recovery_code_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            UserRecoveryCodeRotateRequest(
                recovery_code="SHORT",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("recovery_code",))
        self.assertEqual(error["type"], "string_too_short")


class TestUserRecoveryCodeRotateResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = UserRecoveryCodeRotateResponse(
            recovery_code=_CANON,
        )
        self.assertEqual(resp.recovery_code, _CANON)
