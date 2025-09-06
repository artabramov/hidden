import re
import pyotp
import unittest
from app.helpers.mfa_helper import generate_mfa_secret, calculate_totp

BASE32_RE = re.compile(r"^[A-Z2-7]+$")


class MFAHelperTest(unittest.TestCase):
    def test_generate_mfa_secret_min_length(self):
        secret = generate_mfa_secret()
        self.assertRegex(secret, BASE32_RE)
        self.assertGreaterEqual(len(secret), 16)

    def test_generate_mfa_secret_uniqueness(self):
        seen = set()
        for _ in range(100):
            s = generate_mfa_secret()
            self.assertNotIn(s, seen)
            seen.add(s)

    def test_generate_mfa_secret_with_totp(self):
        secret = generate_mfa_secret()
        totp = pyotp.TOTP(secret)

        code = totp.now()
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), 6)
        self.assertTrue(totp.verify(code))

    def test_generate_mfa_secret_provisioning_uri_build(self):
        secret = generate_mfa_secret()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name="user@example.com", issuer_name="Hidden")
        self.assertIn("otpauth://totp/", uri)
        self.assertIn("issuer=Hidden", uri)
        self.assertIn("user%40example.com", uri)

    def test_generate_mfa_secret_no_padding(self):
        secret = generate_mfa_secret()
        self.assertNotIn("=", secret)

    def test_generate_mfa_secret_provisioning_uri_unicode_and_spaces(self):
        secret = generate_mfa_secret()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name="Иван Петров", issuer_name="Hidden App")
        self.assertIn("otpauth://totp/", uri)
        self.assertIn("issuer=Hidden%20App", uri)
        self.assertTrue("%20" in uri or "%D0" in uri)

    def test_calculate_totp_returns_6_digit_string(self):
        secret = "JBSWY3DPEHPK3PXP"
        code = calculate_totp(secret)
        self.assertIsInstance(code, str)
        self.assertRegex(code, r"^\d{6}$")

    def test_calculate_totp_format_is_6_digits(self):
        secret = "JBSWY3DPEHPK3PXP"
        code = calculate_totp(secret)
        self.assertIsInstance(code, str)
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_calculate_totp_raises_on_invalid_secret(self):
        with self.assertRaises(Exception):
            calculate_totp("not-base32!!!")

    def test_calculate_totp_raises_on_non_string_secret(self):
        with self.assertRaises(Exception):
            calculate_totp(None)

    def test_calculate_totp_raises_on_empty_secret(self):
        with self.assertRaises(Exception):
            calculate_totp("")
