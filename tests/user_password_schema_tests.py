import unittest
from pydantic import ValidationError
from app.schemas.user_password_schema import UserPasswordRequest


class UserPasswordSchemaTest(unittest.TestCase):

    def test_current_password_empty(self):
        data = {
            "current_password": "",
            "updated_password": "Qwer2!",
        }
        with self.assertRaises(ValidationError):
            UserPasswordRequest(**data)

    def test_current_password_too_short(self):
        data = {
            "current_password": "Qwe1!",
            "updated_password": "Qwer2!",
        }
        with self.assertRaises(ValidationError):
            UserPasswordRequest(**data)

    def test_current_password_length_min(self):
        data = {
            "current_password": "Qwer1!",
            "updated_password": "Qwer2!",
        }
        schema = UserPasswordRequest(**data)
        self.assertEqual(schema.current_password, "Qwer1!")
        self.assertEqual(schema.updated_password, "Qwer2!")

    def test_updated_password_empty(self):
        data = {
            "current_password": "Qwer1!",
            "updated_password": "",
        }
        with self.assertRaises(ValidationError):
            UserPasswordRequest(**data)

    def test_updated_password_too_short(self):
        data = {
            "current_password": "Qwer1!",
            "updated_password": "Qwe2!",
        }
        with self.assertRaises(ValidationError):
            UserPasswordRequest(**data)

    def test_updated_password_length_min(self):
        data = {
            "current_password": "Qwer1!",
            "updated_password": "Qwer2!",
        }
        schema = UserPasswordRequest(**data)
        self.assertEqual(schema.current_password, "Qwer1!")
        self.assertEqual(schema.updated_password, "Qwer2!")


if __name__ == "__main__":
    unittest.main()
