import unittest
from app.validators.user_validators import (
    username_validate, password_validate, totp_validate, role_validate,
    summary_validate
)


class UserValidatorsTest(unittest.TestCase):

    def test_username_correct(self):
        cases = [
            ("john", "john"),
            ("JOHN", "john"),
            ("john_doe", "john_doe"),
            ("j0hn", "j0hn"),
            ("a2_", "a2_"),
            ("__user__", "__user__"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(username_validate(raw), expected)

    def test_username_invalid(self):
        cases = [
            "john-doe", "john.doe", "john@doe", "джон", "john doe", "john!"]
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    username_validate(raw)

    def test_username_length_enforced_by_schema(self):
        self.assertEqual(username_validate("a"), "a")

    def test_password_valid(self):
        cases = [
            "Aa1!aa",
            "Zz9#MoreChars",
            "Passw0rd!",
            "A1!aaaaa",
            "Strong_P@ssw0rd",
        ]
        for pwd in cases:
            with self.subTest(pwd=pwd):
                self.assertEqual(password_validate(pwd), pwd)

    def test_password_reject_spaces(self):
        with self.assertRaises(ValueError):
            password_validate("Aa1! a")

    def test_password_requires_lowercase(self):
        with self.assertRaises(ValueError):
            password_validate("AA1!AAA")

    def test_password_requires_uppercase(self):
        with self.assertRaises(ValueError):
            password_validate("aa1!aaa")

    def test_password_requires_digit(self):
        with self.assertRaises(ValueError):
            password_validate("Aa!aaaa")

    def test_password_requires_special(self):
        with self.assertRaises(ValueError):
            password_validate("Aa1aaaa")

    def test_password_special_set_coverage_examples(self):
        for ch in "!@#$%^&*()_+={}[]:;'<>,.?/\\|-":
            pwd = f"Aa1{ch}aaaa"
            with self.subTest(ch=ch):
                self.assertEqual(password_validate(pwd), pwd)

    def test_summary_none(self):
        self.assertIsNone(summary_validate(None))

    def test_summary_blank_to_none(self):
        self.assertIsNone(summary_validate(""))
        self.assertIsNone(summary_validate("   "))
        self.assertIsNone(summary_validate("\n\t"))

    def test_summary_trimmed(self):
        self.assertEqual(summary_validate("  hello  "), "hello")
        self.assertEqual(summary_validate("text"), "text")

    def test_role_normalizes_to_lowercase(self):
        cases = [
            ("Admin", "admin"),
            ("EDITOR", "editor"),
            ("WrItEr", "writer"),
            ("reader", "reader"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(role_validate(raw), expected)

    def test_role_trims_and_lowercases(self):
        self.assertEqual(role_validate(" Admin "), "admin")
        self.assertEqual(role_validate(" editor "), "editor")

    def test_role_non_string_passthrough(self):
        sentinel = object()
        for raw in [None, 123, sentinel]:
            with self.subTest(raw=raw):
                self.assertIs(role_validate(raw), raw)

    def test_totp_valid_numeric(self):
        cases = ["0", "123456", "9876543210"]
        for totp in cases:
            with self.subTest(totp=totp):
                self.assertEqual(totp_validate(totp), totp)

    def test_totp_invalid_non_numeric(self):
        cases = ["12a456", "12 3456", "123-456", "abc", ""]
        for totp in cases:
            with self.subTest(totp=totp):
                with self.assertRaises(ValueError):
                    totp_validate(totp)
