import unittest
from pydantic import ValidationError
from app.schemas.user_register import UserRegisterRequest, UserRegisterResponse


class UserRegisterSchemaTest(unittest.TestCase):
    def test_request_successful_build_and_normalization(self):
        m = UserRegisterRequest(
            username="John_Doe",
            password="Aa1!aaaa",
            first_name=" John ",
            last_name=" Doe ",
            summary="  Hello  ",
        )
        self.assertEqual(m.first_name, "John")
        self.assertEqual(m.last_name, "Doe")
        self.assertEqual(m.username, "john_doe")
        self.assertEqual(m.password.get_secret_value(), "Aa1!aaaa")
        self.assertEqual(m.summary, "Hello")
        self.assertIn("SecretStr", repr(m))

    def test_request_username_with_outer_spaces_rejected_when_before(self):
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username=" John_Doe ",
                password="Aa1!aaaa",
                first_name="A",
                last_name="B",
            )

    def test_request_username_length_constraints(self):
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="a",
                password="Aa1!aaaa",
                first_name="A",
                last_name="B",
            )
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="a" * 41,
                password="Aa1!aaaa",
                first_name="A",
                last_name="B",
            )

    def test_request_first_last_name_constraints(self):
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="user_1",
                password="Aa1!aaaa",
                first_name="",
                last_name="B",
            )
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="user_1",
                password="Aa1!aaaa",
                first_name="A",
                last_name="",
            )
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="user_1",
                password="Aa1!aaaa",
                first_name="A" * 41,
                last_name="B",
            )

    def test_request_summary_max_length(self):
        ok = "x" * 4096
        m = UserRegisterRequest(
            username="user_1",
            password="Aa1!aaaa",
            first_name="A",
            last_name="B",
            summary=ok,
        )
        self.assertEqual(m.summary, ok)

        too_long = "x" * 4097
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="user_1",
                password="Aa1!aaaa",
                first_name="A",
                last_name="B",
                summary=too_long,
            )

    def test_request_summary_blank_to_none(self):
        m = UserRegisterRequest(
            username="user_1",
            password="Aa1!aaaa",
            first_name="A",
            last_name="B",
            summary="   ",
        )
        self.assertIsNone(m.summary)

    def test_request_password_min_length_and_complexity(self):
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="user_1",
                password="Aa1!",
                first_name="A",
                last_name="B",
            )
        with self.assertRaises(ValidationError):
            UserRegisterRequest(
                username="user_1",
                password="aaaaaaa!",
                first_name="A",
                last_name="B",
            )

    def test_response_success(self):
        r = UserRegisterResponse(user_id=123, mfa_secret="BASE32SECRET")
        self.assertEqual(r.user_id, 123)
        self.assertEqual(r.mfa_secret, "BASE32SECRET")

    def test_response_types_enforced(self):
        with self.assertRaises(ValidationError):
            UserRegisterResponse(user_id="not-int", mfa_secret="X")
