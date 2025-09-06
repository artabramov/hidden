import unittest
import asyncio
from app.models.user import User, UserRole
from unittest.mock import MagicMock


class UserModelTest(unittest.TestCase):
    def _make_user(self, role):
        return User(
            "u",           # username
            "h",           # password_hash
            "Fn",          # first_name
            "Ln",          # last_name
            role,          # role
            True,          # active
            "mfa",         # mfa_secret_encrypted
            "jti",         # jti_encrypted
            summary="s",
        )

    def test_admin_role(self):
        u = self._make_user(UserRole.admin)
        self.assertTrue(u.can_admin)
        self.assertTrue(u.can_edit)
        self.assertTrue(u.can_write)
        self.assertTrue(u.can_read)

    def test_editor_role(self):
        u = self._make_user(UserRole.editor)
        self.assertFalse(u.can_admin)
        self.assertTrue(u.can_edit)
        self.assertTrue(u.can_write)
        self.assertTrue(u.can_read)

    def test_writer_role(self):
        u = self._make_user(UserRole.writer)
        self.assertFalse(u.can_admin)
        self.assertFalse(u.can_edit)
        self.assertTrue(u.can_write)
        self.assertTrue(u.can_read)

    def test_reader_role(self):
        u = self._make_user(UserRole.reader)
        self.assertFalse(u.can_admin)
        self.assertFalse(u.can_edit)
        self.assertFalse(u.can_write)
        self.assertTrue(u.can_read)

    def test_full_name(self):
        u = self._make_user(UserRole.reader)
        self.assertEqual(u.full_name, "Fn Ln")

    def test_constructor_without_summary_sets_none(self):
        u = User("u", "h", "Fn", "Ln", UserRole.reader, True, "mfa", "jti")
        self.assertIsNone(u.summary)

    def test_to_dict(self):
        u = self._make_user(UserRole.reader)
        u.id = 1
        u.created_date = 1111111111
        u.last_login_date = 0
        u.user_thumbnail = MagicMock()
        d = asyncio.run(u.to_dict())
        self.assertEqual(
            set(d.keys()),
            {
                "id",
                "created_date",
                "last_login_date",
                "role",
                "active",
                "username",
                "first_name",
                "last_name",
                "summary",
                "has_thumbnail",
            },
        )
        self.assertEqual(d["id"], 1)
        self.assertEqual(d["created_date"], 1111111111)
        self.assertEqual(d["last_login_date"], 0)
        self.assertEqual(d["role"], UserRole.reader)
        self.assertTrue(d["active"])
        self.assertEqual(d["username"], "u")
        self.assertEqual(d["first_name"], "Fn")
        self.assertEqual(d["last_name"], "Ln")
        self.assertEqual(d["summary"], "s")
        self.assertEqual(d["has_thumbnail"], True)
