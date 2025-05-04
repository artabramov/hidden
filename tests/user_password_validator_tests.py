import unittest
from app.validators.user_password_validator import user_password_validate


class UserPasswordValidatorTest(unittest.TestCase):

    def test_password_validator_whitespaces(self):
        with self.assertRaises(ValueError):
            user_password_validate("Qw1! ")

    def test_password_validator_uppercase_missing(self):
        with self.assertRaises(ValueError):
            user_password_validate("w1!")

    def test_password_validator_lowercase_missing(self):
        with self.assertRaises(ValueError):
            user_password_validate("Q1!")

    def test_password_validator_digit_missing(self):
        with self.assertRaises(ValueError):
            user_password_validate("Qw!")

    def test_password_validator_special_missing(self):
        with self.assertRaises(ValueError):
            user_password_validate("Qw1")

    def test_password_validator_correct(self):
        password = user_password_validate("Qw1!")
        self.assertEqual(password, "Qw1!")


if __name__ == "__main__":
    unittest.main()
