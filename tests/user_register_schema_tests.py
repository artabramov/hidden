import unittest
from pydantic import ValidationError
from app.schemas.user_register_schema import UserRegisterRequest


class UserRegisterSchemaTest(unittest.TestCase):

    def test_username_empty(self):
        data = {
            "username": "",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_username_too_short(self):
        data = {
            "username": "a",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_username_too_long(self):
        data = {
            "username": "a" * 48,
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_username_length_min(self):
        data = {
            "username": "qwer",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe"
        }
        res = UserRegisterRequest(**data)
        self.assertEqual(res.username, data["username"])

    def test_username_length_max(self):
        data = {
            "username": "q" * 47,
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe"
        }
        res = UserRegisterRequest(**data)
        self.assertEqual(res.username, data["username"])

    def test_password_empty(self):
        data = {
            "username": "johndoe",
            "password": "",
            "first_name": "John",
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_password_too_short(self):
        data = {
            "username": "johndoe",
            "password": "Qwe1!",
            "first_name": "John",
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_password_length_min(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe"
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.password, "Qwer1!")

    def test_first_name_empty(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "",
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_first_name_whitespaces(self):
        data = {
            "username": "    ",
            "password": "Qwer1!",
            "first_name": "",
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_first_name_strip(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "  John  ",
            "last_name": "Doe",
            "user_summary": "lorem ipsum"
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.first_name, "John")

    def test_first_name_too_long(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "a" * 48,
            "last_name": "Doe"
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_first_name_length_min(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "Jo",
            "last_name": "Doe",
            "user_summary": "lorem ipsum"
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.first_name, "Jo")

    def test_first_name_length_max(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "J" * 47,
            "last_name": "Doe",
            "user_summary": "lorem ipsum"
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.first_name, "J" * 47)

    def test_last_name_empty(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": ""
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_last_name_whitespaces(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "    "
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_last_name_strip(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "  John  ",
            "last_name": "    Doe    ",
            "user_summary": "lorem ipsum"
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.last_name, "Doe")

    def test_last_name_too_long(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "a" * 1024
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_last_name_length_min(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "  John  ",
            "last_name": "Do",
            "user_summary": "lorem ipsum"
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.last_name, "Do")

    def test_last_name_length_max(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "  John  ",
            "last_name": "D" * 47,
            "user_summary": "lorem ipsum"
        }
        user = UserRegisterRequest(**data)
        self.assertEqual(user.last_name, "D" * 47)

    def test_user_summary_empty(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": ""
        }
        schema = UserRegisterRequest(**data)
        self.assertIsNone(schema.user_summary)

    def test_user_summary_whitespaces(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "    "
        }
        user = UserRegisterRequest(**data)
        self.assertIsNone(user.user_summary)

    def test_user_summary_strip(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "  Lorem ipsum  "
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.user_summary, "Lorem ipsum")

    def test_user_summary_too_long(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "a" * 4096
        }
        with self.assertRaises(ValidationError):
            UserRegisterRequest(**data)

    def test_user_summary_length_max(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "s" * 4095
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.user_summary, "s" * 4095)

    def test_success(self):
        data = {
            "username": "johndoe",
            "password": "Qwer1!",
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "Lorem ipsum"
        }
        schema = UserRegisterRequest(**data)
        self.assertEqual(schema.username, "johndoe")
        self.assertEqual(schema.password, "Qwer1!")
        self.assertEqual(schema.first_name, "John")
        self.assertEqual(schema.last_name, "Doe")
        self.assertEqual(schema.user_summary, "Lorem ipsum")


if __name__ == "__main__":
    unittest.main()
