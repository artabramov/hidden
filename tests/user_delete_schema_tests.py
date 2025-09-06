import unittest
from pydantic import ValidationError
from app.schemas.user_delete import UserDeleteResponse


class UserDeleteResponseSchemaTest(unittest.TestCase):
    def test_valid_response(self):
        m = UserDeleteResponse(user_id=123)
        self.assertEqual(m.user_id, 123)

    def test_user_id_coercion_from_str(self):
        m = UserDeleteResponse(user_id="42")
        self.assertEqual(m.user_id, 42)

    def test_missing_user_id_raises(self):
        with self.assertRaises(ValidationError):
            UserDeleteResponse()

    def test_reject_non_numeric_user_id(self):
        with self.assertRaises(ValidationError):
            UserDeleteResponse(user_id="not-a-number")
