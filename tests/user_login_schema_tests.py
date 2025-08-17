import unittest
from pydantic import ValidationError
from app.schemas.user_login_schema import UserLoginRequest


class UserLoginSchemaTest(unittest.TestCase):

    def test_username_empty(self):
        data = {
            "username": "",
            "password": "Qwer1!",
        }
        with self.assertRaises(ValidationError):
            UserLoginRequest(**data)

    def test_username_too_short(self):
        data = {
            "username": "a",
            "password": "Qwer1!",
        }
        with self.assertRaises(ValidationError):
            UserLoginRequest(**data)

    def test_username_too_long(self):
        data = {
            "username": "a" * 48,
            "password": "Qwer1!",
        }
        with self.assertRaises(ValidationError):
            UserLoginRequest(**data)

    def test_username_length_min(self):
        data = {
            "username": "aa",
            "password": "Qwer1!",
        }
        res = UserLoginRequest(**data)
        self.assertEqual(res.username, "aa")

    def test_username_length_max(self):
        data = {
            "username": "a" * 40,
            "password": "Qwer1!",
        }
        res = UserLoginRequest(**data)
        self.assertEqual(res.username, "a" * 40)

    def test_username_to_lowercase(self):
        data = {
            "username": "QwErTy",
            "password": "Qwer1!",
        }
        res = UserLoginRequest(**data)
        self.assertEqual(res.username, "qwerty")

    def test_password_empty(self):
        data = {
            "username": "johndoe",
            "password": "",
        }
        with self.assertRaises(ValidationError):
            UserLoginRequest(**data)

    def test_password_too_short(self):
        data = {
            "username": "johndoe",
            "password": "Qwe1!",
        }
        with self.assertRaises(ValidationError):
            UserLoginRequest(**data)

    def test_password_length_min(self):
        data = {
            "username": "qwerty",
            "password": "Qwer1!",
        }
        res = UserLoginRequest(**data)
        self.assertEqual(res.password, "Qwer1!")


if __name__ == "__main__":
    unittest.main()
