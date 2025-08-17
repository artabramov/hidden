import unittest
from pydantic import ValidationError
from app.schemas.user_update_schema import UserUpdateRequest


class UserUpdateRequestTest(unittest.TestCase):

    def test_first_name_missing(self):
        data = {
            "last_name": "Doe",
            "user_summary": "Lorem ipsum",
        }

        with self.assertRaises(ValidationError):
            UserUpdateRequest(**data)

    def test_first_name_length_min(self):
        data = {
            "first_name": "J",
            "last_name": "Doe",
            "user_summary": "Lorem ipsum",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.first_name, "J")

    def test_first_name_length_max(self):
        data = {
            "first_name": "J" * 47,
            "last_name": "Doe",
            "user_summary": "Lorem ipsum",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.first_name, "J" * 47)

    def test_first_name_too_short(self):
        data = {
            "first_name": "",
            "last_name": "Doe",
            "user_summary": "Lorem ipsum",
        }

        with self.assertRaises(ValidationError):
            UserUpdateRequest(**data)

    def test_first_name_too_long(self):
        data = {
            "first_name": "J" * 48,
            "last_name": "D",
            "user_summary": "Lorem ipsum",
        }

        with self.assertRaises(ValidationError):
            UserUpdateRequest(**data)

    def test_first_name_strip(self):
        data = {
            "first_name": "  John  ",
            "last_name": "Doe",
            "user_summary": "Lorem ipsum",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.first_name, "John")

    def test_last_name_missing(self):
        data = {
            "first_name": "John",
            "user_summary": "Lorem ipsum",
        }

        with self.assertRaises(ValidationError):
            UserUpdateRequest(**data)

    def test_last_name_length_min(self):
        data = {
            "first_name": "J",
            "last_name": "Do",
            "user_summary": "Lorem ipsum",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.last_name, "Do")

    def test_last_name_length_max(self):
        data = {
            "first_name": "John",
            "last_name": "D" * 47,
            "user_summary": "Lorem ipsum",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.last_name, "D" * 47)

    def test_last_name_too_short(self):
        data = {
            "first_name": "",
            "last_name": "D",
            "user_summary": "Lorem ipsum",
        }

        with self.assertRaises(ValidationError):
            UserUpdateRequest(**data)

    def test_last_name_too_long(self):
        data = {
            "first_name": "John",
            "last_name": "D" * 48,
            "user_summary": "Lorem ipsum",
        }

        with self.assertRaises(ValidationError):
            UserUpdateRequest(**data)

    def test_last_name_strip(self):
        data = {
            "first_name": "John",
            "last_name": "  Doe  ",
            "user_summary": "Lorem ipsum",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.last_name, "Doe")

    def test_user_summary_none(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertIsNone(user.user_summary)

    def test_user_summary_too_long(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "a" * 4096
        }

        with self.assertRaises(ValidationError):
            UserUpdateRequest(**data)

    def test_user_summary_length_max(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "a" * 4095
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.user_summary, "a" * 4095)

    def test_user_summary_strip(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "  Lorem ipsum  "
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.user_summary, "Lorem ipsum")

    def test_user_summary_whitespaces(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "    "
        }

        user = UserUpdateRequest(**data)
        self.assertIsNone(user.user_summary)

    def test_request_correct(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "user_summary": "Lorem ipsum",
        }

        user = UserUpdateRequest(**data)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.user_summary, "Lorem ipsum")


if __name__ == "__main__":
    unittest.main()
