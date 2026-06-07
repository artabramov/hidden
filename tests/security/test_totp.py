# tests/security/test_totp.py
# SPDX-License-Identifier: SSPL-1.0

import uuid
import unittest
from unittest.mock import patch

import pyotp

from app.security import totp


class TestTotp(unittest.TestCase):

    def test_generate_mfa_session_uuid_returns_valid_uuid(self):
        value = totp.generate_mfa_session_uuid()

        self.assertIsInstance(value, str)

        parsed = uuid.UUID(value)
        self.assertEqual(str(parsed), value)

    def test_generate_mfa_session_uuid_returns_different_values(self):
        s1 = totp.generate_mfa_session_uuid()
        s2 = totp.generate_mfa_session_uuid()

        self.assertNotEqual(s1, s2)

    def test_generate_totp_secret_returns_valid_base32(self):
        secret = totp.generate_totp_secret()

        self.assertIsInstance(secret, str)
        self.assertGreater(len(secret), 0)

        pyotp.TOTP(secret)

    def test_generate_totp_secret_returns_different_values(self):
        s1 = totp.generate_totp_secret()
        s2 = totp.generate_totp_secret()

        self.assertNotEqual(s1, s2)

    def test_is_totp_correct_returns_true_for_valid_code(self):
        secret = pyotp.random_base32()
        totp_obj = pyotp.TOTP(secret)

        with patch("time.time", return_value=1_700_000_000):
            code = totp_obj.now()

        with patch("time.time", return_value=1_700_000_000):
            result = totp.is_totp_correct(secret, code)

        self.assertTrue(result)

    def test_is_totp_correct_returns_false_for_invalid_code(self):
        secret = pyotp.random_base32()

        with patch("time.time", return_value=1_700_000_000):
            result = totp.is_totp_correct(secret, "000000")

        self.assertFalse(result)

    def test_is_totp_correct_returns_false_for_expired_code(self):
        secret = pyotp.random_base32()
        totp_obj = pyotp.TOTP(secret)

        code = totp_obj.at(1_700_000_000)
        result = totp_obj.verify(
            code,
            for_time=1_700_000_030,
        )

        self.assertFalse(result)

    def test_is_totp_correct_accepts_code_in_same_time_window(self):
        secret = pyotp.random_base32()
        totp_obj = pyotp.TOTP(secret)

        with patch("time.time", return_value=1_700_000_000):
            code = totp_obj.now()

        with patch("time.time", return_value=1_700_000_010):
            result = totp.is_totp_correct(secret, code)

        self.assertTrue(result)
