# tests/models/test_audit.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.models.audit import Audit, prevent_delete, prevent_update


class TestAuditModel(unittest.TestCase):

    def test_table_name(self):
        self.assertEqual(Audit.__tablename__, "audit")

    def test_id_column_configuration(self):
        column = Audit.__table__.columns["id"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.primary_key)
        self.assertEqual(str(column.type), "INTEGER")

    def test_created_at_column_configuration(self):
        column = Audit.__table__.columns["created_at"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertIsNotNone(column.default)
        self.assertEqual(str(column.type), "INTEGER")

    def test_created_by_column_configuration(self):
        column = Audit.__table__.columns["created_by"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_event_column_configuration(self):
        column = Audit.__table__.columns["event"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(str(column.type), "VARCHAR(128)")

    def test_request_uuid_column_configuration(self):
        column = Audit.__table__.columns["request_uuid"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(str(column.type), "VARCHAR(64)")

    def test_resource_type_column_configuration(self):
        column = Audit.__table__.columns["resource_type"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(str(column.type), "VARCHAR(64)")

    def test_resource_id_column_configuration(self):
        column = Audit.__table__.columns["resource_id"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(str(column.type), "INTEGER")

    def test_table_has_sqlite_autoincrement(self):
        self.assertTrue(
            Audit.__table__.dialect_options["sqlite"]["autoincrement"]
        )

    def test_prevent_update_raises_runtime_error(self):
        with self.assertRaises(RuntimeError) as cm:
            prevent_update(None, None, None)

        self.assertEqual(
            str(cm.exception),
            "Audit records cannot be updated",
        )

    def test_prevent_delete_raises_runtime_error(self):
        with self.assertRaises(RuntimeError) as cm:
            prevent_delete(None, None, None)

        self.assertEqual(
            str(cm.exception),
            "Audit records cannot be deleted",
        )
