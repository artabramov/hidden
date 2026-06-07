# tests/models/test_variable.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.models.user import User
from app.models.variable import Variable


class TestVariableModel(unittest.TestCase):

    def test_variable_table_name(self):
        self.assertEqual(Variable.__tablename__, "variables")

    def test_namespace_column_configuration(self):
        column = Variable.__table__.columns["namespace"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)

    def test_variable_key_column_configuration(self):
        column = Variable.__table__.columns["variable_key"]

        self.assertFalse(column.nullable)

    def test_variable_value_column_configuration(self):
        column = Variable.__table__.columns["variable_value"]

        self.assertFalse(column.nullable)

    def test_created_by_column_configuration(self):
        column = Variable.__table__.columns["created_by"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_updated_by_column_configuration(self):
        column = Variable.__table__.columns["updated_by"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_created_at_column_configuration(self):
        column = Variable.__table__.columns["created_at"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)

    def test_updated_at_column_configuration(self):
        column = Variable.__table__.columns["updated_at"]

        self.assertTrue(column.nullable)

    def test_variable_table_has_unique_index(self):
        index_names = {index.name for index in Variable.__table__.indexes}
        self.assertIn("uq_variables_namespace_variable_key", index_names)

    def test_variable_unique_index_uses_namespace_and_key(self):
        indexes = {
            index.name: index
            for index in Variable.__table__.indexes
        }

        index = indexes["uq_variables_namespace_variable_key"]
        expressions = [str(expr) for expr in index.expressions]

        self.assertEqual(len(expressions), 2)
        self.assertIn("variables.namespace", expressions[0])
        self.assertIn("variables.variable_key", expressions[1])

    def test_variable_table_has_sqlite_autoincrement(self):
        self.assertTrue(Variable.__table__.dialect_options["sqlite"])
        self.assertTrue(
            Variable.__table__.dialect_options["sqlite"]["autoincrement"]
        )

    def test_relationship_variable_and_created_by_user(self):
        user = User(
            id=1,
            username="alice",
            password_hash="hash",
            totp_secret_encrypted="secret",
            display_name="Alice",
        )
        variable = Variable(
            id=1,
            namespace="thumbnails",
            variable_key="max_width",
            variable_value="320",
            created_by=1,
        )

        variable.variable_created_by_user = user

        self.assertIs(variable.variable_created_by_user, user)

    def test_relationship_variable_and_updated_by_user(self):
        user = User(
            id=2,
            username="bob",
            password_hash="hash",
            totp_secret_encrypted="secret",
            display_name="Bob",
        )
        variable = Variable(
            id=1,
            namespace="thumbnails",
            variable_key="max_width",
            variable_value="320",
            updated_by=2,
        )

        variable.variable_updated_by_user = user

        self.assertIs(variable.variable_updated_by_user, user)

    def test_variable_created_by_user_relationship_configuration(self):
        rel = Variable.__mapper__.relationships["variable_created_by_user"]

        self.assertEqual(rel.key, "variable_created_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_variable_created_by_user_primaryjoin(self):
        rel = Variable.__mapper__.relationships["variable_created_by_user"]

        join = str(rel.primaryjoin)

        self.assertIn("variables.created_by", join)
        self.assertIn("users.id", join)

    def test_variable_created_by_user_target_model(self):
        rel = Variable.__mapper__.relationships["variable_created_by_user"]

        self.assertEqual(rel.mapper.class_, User)

    def test_variable_created_by_user_has_no_back_populates(self):
        rel = Variable.__mapper__.relationships["variable_created_by_user"]

        self.assertIsNone(rel.back_populates)

    def test_variable_updated_by_user_relationship_configuration(self):
        rel = Variable.__mapper__.relationships["variable_updated_by_user"]

        self.assertEqual(rel.key, "variable_updated_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_variable_updated_by_user_primaryjoin(self):
        rel = Variable.__mapper__.relationships["variable_updated_by_user"]

        join = str(rel.primaryjoin)

        self.assertIn("variables.updated_by", join)
        self.assertIn("users.id", join)

    def test_variable_updated_by_user_target_model(self):
        rel = Variable.__mapper__.relationships["variable_updated_by_user"]

        self.assertEqual(rel.mapper.class_, User)

    def test_variable_updated_by_user_has_no_back_populates(self):
        rel = Variable.__mapper__.relationships["variable_updated_by_user"]

        self.assertIsNone(rel.back_populates)
