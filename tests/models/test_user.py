# tests/models/test_user.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.models.user import User, UserRole


class TestUserRole(unittest.TestCase):
    def test_reader_value(self):
        self.assertEqual(UserRole.READER.value, "reader")

    def test_writer_value(self):
        self.assertEqual(UserRole.WRITER.value, "writer")

    def test_editor_value(self):
        self.assertEqual(UserRole.EDITOR.value, "editor")

    def test_admin_value(self):
        self.assertEqual(UserRole.ADMIN.value, "admin")


class TestUserModel(unittest.TestCase):
    def test_table_name(self):
        self.assertEqual(User.__tablename__, "users")

    def test_can_read_for_reader(self):
        user = User()
        user.role = UserRole.READER.value

        self.assertTrue(user.can_read)
        self.assertFalse(user.can_write)
        self.assertFalse(user.can_edit)
        self.assertFalse(user.can_admin)

    def test_can_read_for_writer(self):
        user = User()
        user.role = UserRole.WRITER.value

        self.assertTrue(user.can_read)
        self.assertTrue(user.can_write)
        self.assertFalse(user.can_edit)
        self.assertFalse(user.can_admin)

    def test_can_read_for_editor(self):
        user = User()
        user.role = UserRole.EDITOR.value

        self.assertTrue(user.can_read)
        self.assertTrue(user.can_write)
        self.assertTrue(user.can_edit)
        self.assertFalse(user.can_admin)

    def test_can_read_for_admin(self):
        user = User()
        user.role = UserRole.ADMIN.value

        self.assertTrue(user.can_read)
        self.assertTrue(user.can_write)
        self.assertTrue(user.can_edit)
        self.assertTrue(user.can_admin)

    def test_permissions_for_unknown_role(self):
        user = User()
        user.role = "unknown"

        self.assertFalse(user.can_read)
        self.assertFalse(user.can_write)
        self.assertFalse(user.can_edit)
        self.assertFalse(user.can_admin)

    def test_table_has_check_constraint(self):
        constraints = list(User.__table__.constraints)
        names = {constraint.name for constraint in constraints}

        self.assertIn("ck_users_role", names)

    def test_check_constraint_sqltext(self):
        constraint = next(
            constraint
            for constraint in User.__table__.constraints
            if constraint.name == "ck_users_role"
        )

        self.assertIn(
            "role IN ('reader', 'writer', 'editor', 'admin')",
            str(constraint.sqltext),
        )

    def test_table_has_sqlite_autoincrement(self):
        self.assertTrue(
            User.__table__.dialect_options["sqlite"]["autoincrement"]
        )

    def test_role_column_properties(self):
        column = User.__table__.columns["role"]

        self.assertFalse(column.nullable)
        self.assertEqual(str(column.type), "VARCHAR(16)")
        self.assertIsNotNone(column.server_default)
        self.assertIn("'reader'", str(column.server_default.arg))

    def test_username_column_properties(self):
        column = User.__table__.columns["username"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.unique)
        self.assertEqual(str(column.type), "VARCHAR(40)")

    def test_display_name_column_properties(self):
        column = User.__table__.columns["display_name"]

        self.assertFalse(column.nullable)
        self.assertEqual(str(column.type), "VARCHAR(40)")

    def test_summary_column_properties(self):
        column = User.__table__.columns["summary"]

        self.assertTrue(column.nullable)
        self.assertEqual(str(column.type), "VARCHAR(4096)")

    def test_is_active_column_properties(self):
        column = User.__table__.columns["is_active"]

        self.assertFalse(column.nullable)
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_failed_password_attempts_column_properties(self):
        column = User.__table__.columns["failed_password_attempts"]

        self.assertFalse(column.nullable)
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_failed_totp_attempts_column_properties(self):
        column = User.__table__.columns["failed_totp_attempts"]

        self.assertFalse(column.nullable)
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_recovery_code_hash_not_nullable(self):
        column = User.__table__.columns["recovery_code_hash"]

        self.assertFalse(column.nullable)
        self.assertEqual(str(column.type), "VARCHAR(255)")

    def test_failed_recovery_code_attempts_column_properties(self):
        column = User.__table__.columns["failed_recovery_code_attempts"]

        self.assertFalse(column.nullable)
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_current_jti_encrypted_nullable(self):
        column = User.__table__.columns["current_jti_encrypted"]

        self.assertTrue(column.nullable)

    def test_password_hash_not_nullable(self):
        column = User.__table__.columns["password_hash"]

        self.assertFalse(column.nullable)

    def test_totp_secret_encrypted_not_nullable(self):
        column = User.__table__.columns["totp_secret_encrypted"]

        self.assertFalse(column.nullable)

    def test_mfa_session_uuid_column_properties(self):
        column = User.__table__.columns["mfa_session_uuid"]

        self.assertTrue(column.nullable)
        self.assertEqual(str(column.type), "VARCHAR(80)")
        self.assertTrue(column.unique)

    def test_created_at_has_default_and_index(self):
        column = User.__table__.columns["created_at"]

        self.assertFalse(column.nullable)
        self.assertIsNotNone(column.default)

        index_names = {index.name for index in User.__table__.indexes}
        self.assertTrue(any("created_at" in name for name in index_names))

    def test_updated_at_nullable(self):
        column = User.__table__.columns["updated_at"]

        self.assertTrue(column.nullable)

    def test_role_and_display_name_indexes_exist(self):
        index_names = {index.name for index in User.__table__.indexes}

        self.assertTrue(any("role" in name for name in index_names))
        self.assertTrue(any("display_name" in name for name in index_names))

    def test_password_verified_at_nullable(self):
        column = User.__table__.columns["password_verified_at"]

        self.assertTrue(column.nullable)
        self.assertEqual(str(column.type), "INTEGER")

    def test_suspended_until_nullable(self):
        column = User.__table__.columns["suspended_until"]

        self.assertTrue(column.nullable)
        self.assertEqual(str(column.type), "INTEGER")

    def test_last_authenticated_at_nullable(self):
        column = User.__table__.columns["last_authenticated_at"]

        self.assertTrue(column.nullable)
        self.assertEqual(str(column.type), "INTEGER")

    def test_id_column_properties(self):
        column = User.__table__.columns["id"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.primary_key)
        self.assertEqual(str(column.type), "INTEGER")

    def test_created_at_column_type(self):
        column = User.__table__.columns["created_at"]

        self.assertEqual(str(column.type), "INTEGER")

    def test_updated_at_column_type(self):
        column = User.__table__.columns["updated_at"]

        self.assertEqual(str(column.type), "INTEGER")

    def test_username_not_indexed(self):
        index_names = {index.name for index in User.__table__.indexes}

        self.assertFalse(any("username" in name for name in index_names))

    def test_username_is_unique(self):
        column = User.__table__.columns["username"]

        self.assertTrue(column.unique)

    def test_last_authenticated_at_not_indexed(self):
        index_names = {index.name for index in User.__table__.indexes}

        self.assertFalse(
            any("last_authenticated_at" in name for name in index_names)
        )

    def test_password_verified_at_not_indexed(self):
        index_names = {index.name for index in User.__table__.indexes}

        self.assertFalse(
            any("password_verified_at" in name for name in index_names)
        )
