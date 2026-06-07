# tests/models/test_file_tag.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.models.file import File  # noqa: F401
from app.models.file_tag import FileTag
from app.models.user import User


class TestFileTagModel(unittest.TestCase):

    def test_file_tag_table_name(self):
        self.assertEqual(FileTag.__tablename__, "files_tags")

    def test_file_id_column_configuration(self):
        column = FileTag.__table__.columns["file_id"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "files.id")
        self.assertEqual(fk.ondelete, "CASCADE")

    def test_created_by_column_configuration(self):
        column = FileTag.__table__.columns["created_by"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_created_at_column_configuration(self):
        column = FileTag.__table__.columns["created_at"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)

    def test_tag_column_is_required(self):
        column = FileTag.__table__.columns["tag"]

        self.assertFalse(column.nullable)

    def test_file_tag_table_has_unique_index(self):
        index_names = {index.name for index in FileTag.__table__.indexes}
        self.assertIn("uq_files_tags_file_id_tag", index_names)

    def test_file_tag_unique_index_uses_lower_for_case_insensitive_tag(self):
        indexes = {
            index.name: index
            for index in FileTag.__table__.indexes
        }

        index = indexes["uq_files_tags_file_id_tag"]
        expressions = [str(expr) for expr in index.expressions]

        self.assertEqual(len(expressions), 2)
        self.assertIn("files_tags.file_id", expressions[0])
        self.assertIn("lower", expressions[1].lower())
        self.assertIn("files_tags.tag", expressions[1])

    def test_file_tag_table_has_sqlite_autoincrement(self):
        self.assertTrue(FileTag.__table__.dialect_options["sqlite"])
        self.assertTrue(
            FileTag.__table__.dialect_options["sqlite"]["autoincrement"]
        )

    def test_relationship_tag_and_file(self):
        file = File(
            id=1,
            filename="file.txt",
            created_by=1,
            checksum="a" * 64,
        )
        tag = FileTag(
            id=1,
            file_id=1,
            created_by=1,
            tag="important",
        )

        tag.tag_file = file

        self.assertIs(tag.tag_file, file)
        self.assertIn(tag, file.file_tags)

    def test_relationship_tag_and_created_by_user(self):
        user = User(
            id=1,
            username="alice",
            password_hash="hash",
            totp_secret_encrypted="secret",
            display_name="Alice",
        )
        tag = FileTag(
            id=1,
            file_id=1,
            created_by=1,
            tag="important",
        )

        tag.tag_created_by_user = user

        self.assertIs(tag.tag_created_by_user, user)

    def test_tag_file_relationship_configuration(self):
        rel = FileTag.__mapper__.relationships["tag_file"]

        self.assertEqual(rel.key, "tag_file")
        self.assertEqual(rel.mapper.class_.__name__, "File")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.back_populates, "file_tags")
        self.assertEqual(rel.lazy, "selectin")
        self.assertTrue(rel.passive_deletes)

    def test_tag_file_primaryjoin(self):
        rel = FileTag.__mapper__.relationships["tag_file"]

        join = str(rel.primaryjoin)

        self.assertIn("files.id", join)
        self.assertIn("files_tags.file_id", join)

    def test_tag_file_target_model(self):
        rel = FileTag.__mapper__.relationships["tag_file"]

        self.assertEqual(rel.mapper.class_, File)

    def test_tag_created_by_user_relationship_configuration(self):
        rel = FileTag.__mapper__.relationships["tag_created_by_user"]

        self.assertEqual(rel.key, "tag_created_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_tag_created_by_user_primaryjoin(self):
        rel = FileTag.__mapper__.relationships["tag_created_by_user"]

        join = str(rel.primaryjoin)

        self.assertIn("files_tags.created_by", join)
        self.assertIn("users.id", join)

    def test_tag_created_by_user_target_model(self):
        rel = FileTag.__mapper__.relationships["tag_created_by_user"]

        self.assertEqual(rel.mapper.class_, User)

    def test_tag_created_by_user_has_no_back_populates(self):
        rel = FileTag.__mapper__.relationships["tag_created_by_user"]

        self.assertIsNone(rel.back_populates)
