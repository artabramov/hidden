import unittest
from pydantic import ValidationError
from app.schemas.user_update import UserUpdateRequest, UserUpdateResponse


class UserUpdateSchemasTest(unittest.TestCase):
    def test_request_valid_and_trimming(self):
        m = UserUpdateRequest(
            first_name="  John  ",
            last_name="  Doe ",
            summary="  hello world  ",
        )
        self.assertEqual(m.first_name, "John")
        self.assertEqual(m.last_name, "Doe")
        self.assertEqual(m.summary, "hello world")

    def test_request_summary_blank_to_none(self):
        m1 = UserUpdateRequest(first_name="John", last_name="Doe", summary="")
        m2 = UserUpdateRequest(first_name="John", last_name="Doe", summary="   ")
        m3 = UserUpdateRequest(first_name="John", last_name="Doe", summary="\n\t")
        self.assertIsNone(m1.summary)
        self.assertIsNone(m2.summary)
        self.assertIsNone(m3.summary)

    def test_request_summary_none_ok(self):
        m = UserUpdateRequest(first_name="John", last_name="Doe", summary=None)
        self.assertIsNone(m.summary)

    def test_request_first_last_min_length(self):
        with self.assertRaises(ValidationError):
            UserUpdateRequest(first_name="", last_name="Doe")
        with self.assertRaises(ValidationError):
            UserUpdateRequest(first_name="John", last_name="")

    def test_request_first_last_max_length(self):
        long = "x" * 41
        with self.assertRaises(ValidationError):
            UserUpdateRequest(first_name=long, last_name="Doe")
        with self.assertRaises(ValidationError):
            UserUpdateRequest(first_name="John", last_name=long)

    def test_request_summary_max_length(self):
        too_long = "x" * 4097
        with self.assertRaises(ValidationError):
            UserUpdateRequest(first_name="John", last_name="Doe", summary=too_long)

    def test_response_valid(self):
        r = UserUpdateResponse(user_id=123)
        self.assertEqual(r.user_id, 123)

    def test_response_user_id_coercion(self):
        r = UserUpdateResponse(user_id="42")
        self.assertEqual(r.user_id, 42)
