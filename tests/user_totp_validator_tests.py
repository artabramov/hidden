import unittest
from app.validators.user_totp_validator import user_totp_validate


class UserTotpValidatorTest(unittest.TestCase):

    def test_totp_letters(self):
        with self.assertRaises(ValueError):
            user_totp_validate("abcdef")

    def test_user_totp_special(self):
        with self.assertRaises(ValueError):
            user_totp_validate("!@#$%^")

    def test_user_totp_correct(self):
        user_totp = user_totp_validate("123456")
        self.assertEqual(user_totp, "123456")


if __name__ == "__main__":
    unittest.main()
