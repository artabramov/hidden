import unittest
from app.validators.user_validators import (
    username_validate, password_validate, totp_validate, role_validate,
    summary_validate)


class UserValidatorsTest(unittest.TestCase):

    def test_username_string_lowercase(self):
        res = username_validate("JOHNDOE")
        self.assertEqual(res, "johndoe")

    def test_username_string_invalid(self):
        usernames = [
            "john-doe", "john.doe", "john@doe", "джон", "джон до",
            "john doe", "john!"]
        for username in usernames:
            with self.assertRaises(ValueError):
                username_validate(username)

    def test_username_string_correct(self):
        usernames = ["john", "john_doe","j0hn", "__john__"]
        for username in usernames:
            res = username_validate(username)
            self.assertEqual(res, username)

    def test_password_string_correct(self):
        passwords = ["Abcdef1!", "aB1_", "Qw3rty@2025", "X9y!z", "GoodPass9#"]
        for password in passwords:
            res = password_validate(password)
            self.assertEqual(res, password)

    def test_password_string_invalid(self):
        passwords = ["Abc1 !", " Abc1!", "Ab c1!"]
        for password in passwords:
            with self.assertRaises(ValueError):
                password_validate(password)

    def test_password_string_requires_lowercase(self):
        with self.assertRaises(ValueError):
            password_validate("ABCDEF1!")

    def test_password_string_requires_uppercase(self):
        with self.assertRaises(ValueError):
            password_validate("abcdef1!")

    def test_password_string_requires_digit(self):
        with self.assertRaises(ValueError):
            password_validate("Abcdef!@")

    def test_password_string_requires_special(self):
        with self.assertRaises(ValueError):
            password_validate("Abcdef12")

    def test_role_none(self):
        res = role_validate(None)
        self.assertIsNone(res)

    def test_role_string_empty(self):
        res = role_validate("")
        self.assertEqual(res, "")

    def test_role_string_whitespaces(self):
        res = role_validate("   ")
        self.assertEqual(res, "")

    def test_role_string_stripped(self):
        res = role_validate(" Admin ")
        self.assertEqual(res, "admin")

    def test_role_string_mixedcase(self):
        res = role_validate("EdItOr")
        self.assertEqual(res, "editor")

    def test_totp_string_digits(self):
        res = totp_validate("123456")
        self.assertEqual(res, "123456")

    def test_totp_string_leading_zeros(self):
        res = totp_validate("000123")
        self.assertEqual(res, "000123")

    def test_totp_string_empty(self):
        with self.assertRaises(ValueError):
            totp_validate("")

    def test_totp_string_with_spaces(self):
        with self.assertRaises(ValueError):
            totp_validate("12 3456")

    def test_totp_string_with_non_digits(self):
        for totp in ["12345a", "12345-", "12_3456", "abc123"]:
            with self.assertRaises(ValueError):
                totp_validate(totp)

    def test_summary_none(self):
        res = summary_validate(None)
        self.assertIsNone(res)

    def test_summary_string_empty(self):
        res = summary_validate("")
        self.assertIsNone(res)

    def test_summary_string_whitespaces(self):
        res = summary_validate("  ")
        self.assertIsNone(res)

    def test_summary_string_stripped(self):
        res = summary_validate(" Hello ")
        self.assertEqual(res, "Hello")
