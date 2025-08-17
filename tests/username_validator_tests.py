import unittest
from app.validators.username_validator import username_validate


class UsernameValidatorTest(unittest.TestCase):

    def test_username_whitespaces(self):
        with self.assertRaises(ValueError):
            username_validate(" ")

    def test_username_cyrillic(self):
        with self.assertRaises(ValueError):
            username_validate("ы")

    def test_username_dash(self):
        with self.assertRaises(ValueError):
            username_validate("-")

    def test_username_underscore(self):
        with self.assertRaises(ValueError):
            username_validate("_")

    def test_username_special(self):
        with self.assertRaises(ValueError):
            username_validate("!")

    def test_username_correct(self):
        username = username_validate("USER123")
        self.assertEqual(username, "user123")


if __name__ == "__main__":
    unittest.main()
