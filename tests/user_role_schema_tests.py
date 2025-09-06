import unittest
from pydantic import ValidationError
from app.schemas.user_role import UserRoleRequest, UserRoleResponse

class UserRoleSchemasTest(unittest.TestCase):
    def test_request_normalizes_and_accepts_literal(self):
        m = UserRoleRequest(role=" Admin ", active=True)
        self.assertEqual(m.role, "admin")
        self.assertTrue(m.active)

    def test_request_rejects_invalid_role(self):
        with self.assertRaises(ValidationError):
            UserRoleRequest(role="owner", is_active=False)

    def test_request_case_insensitive_variants(self):
        for raw in ["EDITOR", " editor ", "EdItOr"]:
            with self.subTest(raw=raw):
                m = UserRoleRequest(role=raw, active=False)
                self.assertEqual(m.role, "editor")

    def test_response_schema(self):
        r = UserRoleResponse(user_id=42)
        self.assertEqual(r.user_id, 42)
