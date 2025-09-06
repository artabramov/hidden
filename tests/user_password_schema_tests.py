import unittest
from pydantic import ValidationError
from app.schemas.user_password import UserPasswordRequest, UserPasswordResponse


class UserPasswordSchemasTest(unittest.TestCase):
    def test_request_valid(self):
        m = UserPasswordRequest(
            current_password="  OldP@ss1  ",
            updated_password="NewP@ss1",
        )
        self.assertEqual(m.current_password, "OldP@ss1")
        self.assertEqual(m.updated_password, "NewP@ss1")

    def test_updated_password_complexity_enforced(self):
        with self.assertRaises(ValidationError):
            UserPasswordRequest(current_password="Valid1!", updated_password="AA1!AAA")
        with self.assertRaises(ValidationError):
            UserPasswordRequest(current_password="Valid1!", updated_password="aa1!aaa")
        with self.assertRaises(ValidationError):
            UserPasswordRequest(current_password="Valid1!", updated_password="Aa!aaaa")
        with self.assertRaises(ValidationError):
            UserPasswordRequest(current_password="Valid1!", updated_password="Aa1aaaa")
        with self.assertRaises(ValidationError):
            UserPasswordRequest(current_password="Valid1!", updated_password="Aa1! a")

    def test_updated_password_min_length_enforced(self):
        with self.assertRaises(ValidationError):
            UserPasswordRequest(current_password="Valid1!", updated_password="Aa1!")

    def test_current_password_min_length_enforced(self):
        with self.assertRaises(ValidationError):
            UserPasswordRequest(current_password="123", updated_password="Aa1!aaaa")

    def test_response_valid(self):
        r = UserPasswordResponse(user_id=123)
        self.assertEqual(r.user_id, 123)

    def test_response_user_id_coercion_from_str(self):
        r = UserPasswordResponse(user_id="42")
        self.assertEqual(r.user_id, 42)

    def test_request_accepts_strict_valid_example(self):
        m = UserPasswordRequest(current_password="OldP@ss1", updated_password="Aa1!aaaa")
        self.assertEqual(m.current_password, "OldP@ss1")
        self.assertEqual(m.updated_password, "Aa1!aaaa")
