import unittest
from pydantic import ValidationError
from app.schemas.user_role_schema import UserRoleRequest


class TestRoleUpdateRequest(unittest.TestCase):

    def test_user_role_admin(self):
        valid_data = {
            "user_role": "admin",
            "is_active": True
        }

        try:
            request = UserRoleRequest(**valid_data)
            self.assertEqual(request.user_role, "admin")
            self.assertTrue(request.is_active)
        except ValidationError as e:
            self.fail(f"Validation failed for admin: {e}")

    def test_user_role_writer(self):
        valid_data = {
            "user_role": "writer",
            "is_active": True
        }

        try:
            request = UserRoleRequest(**valid_data)
            self.assertEqual(request.user_role, "writer")
            self.assertTrue(request.is_active)
        except ValidationError as e:
            self.fail(f"Validation failed for writer: {e}")

    def test_user_role_editor(self):
        valid_data = {
            "user_role": "editor",
            "is_active": True
        }

        try:
            request = UserRoleRequest(**valid_data)
            self.assertEqual(request.user_role, "editor")
            self.assertTrue(request.is_active)
        except ValidationError as e:
            self.fail(f"Validation failed for editor: {e}")

    def test_user_role_reader(self):
        valid_data = {
            "user_role": "reader",
            "is_active": True
        }

        try:
            request = UserRoleRequest(**valid_data)
            self.assertEqual(request.user_role, "reader")
            self.assertTrue(request.is_active)
        except ValidationError as e:
            self.fail(f"Validation failed for reader: {e}")

    def test_user_role_invalid(self):
        invalid_data = {
            "user_role": "invalid_role",
            "is_active": True
        }

        with self.assertRaises(ValidationError):
            UserRoleRequest(**invalid_data)

    def test_user_role_missing(self):
        invalid_data = {
            "is_active": True
        }

        with self.assertRaises(ValidationError):
            UserRoleRequest(**invalid_data)

    def test_is_active_true(self):
        valid_data = {
            "user_role": "editor",
            "is_active": True
        }

        try:
            request = UserRoleRequest(**valid_data)
            self.assertEqual(request.user_role, "editor")
            self.assertTrue(request.is_active)
        except ValidationError as e:
            self.fail(f"Validation failed for is_active=True: {e}")

    def test_is_active_false(self):
        valid_data = {
            "user_role": "editor",
            "is_active": False
        }

        try:
            request = UserRoleRequest(**valid_data)
            self.assertEqual(request.user_role, "editor")
            self.assertFalse(request.is_active)
        except ValidationError as e:
            self.fail(f"Validation failed for is_active=False: {e}")

    def test_is_active_invalid(self):
        invalid_data = {
            "user_role": "reader",
            "is_active": "not_a_bool"
        }

        with self.assertRaises(ValidationError):
            UserRoleRequest(**invalid_data)

    def test_is_active_missing(self):
        invalid_data = {
            "user_role": "writer"
        }

        with self.assertRaises(ValidationError):
            UserRoleRequest(**invalid_data)


if __name__ == "__main__":
    unittest.main()
