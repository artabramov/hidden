# tests/models/test_file_comment.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from app.models.file import File  # noqa: F401
from app.models.file_comment import FileComment
from app.models.user import User


class TestFileCommentModel(unittest.TestCase):

    def test_file_comment_table_name(self):
        self.assertEqual(FileComment.__tablename__, "files_comments")

    def test_file_id_column_configuration(self):
        column = FileComment.__table__.columns["file_id"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "files.id")
        self.assertEqual(fk.ondelete, "CASCADE")

    def test_created_by_column_configuration(self):
        column = FileComment.__table__.columns["created_by"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_body_column_is_required(self):
        column = FileComment.__table__.columns["body"]

        self.assertFalse(column.nullable)

    def test_created_at_column_configuration(self):
        column = FileComment.__table__.columns["created_at"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)

    def test_updated_at_column_configuration(self):
        column = FileComment.__table__.columns["updated_at"]

        self.assertTrue(column.nullable)

    def test_relationship_file_and_comments(self):
        file = File(
            id=1,
            filename="file.txt",
            created_by=1,
            checksum="a" * 64,
        )

        comment = FileComment(
            id=1,
            file_id=1,
            created_by=1,
            body="hello",
        )

        comment.comment_file = file

        self.assertIs(comment.comment_file, file)
        self.assertIn(comment, file.file_comments)

    def test_relationship_comment_created_by_user(self):
        user = User(
            id=1,
            username="u",
            password_hash="x",
            totp_secret_encrypted="x",
            display_name="u",
        )

        comment = FileComment(
            id=1,
            file_id=1,
            created_by=1,
            body="hello",
        )

        comment.comment_created_by_user = user

        self.assertIs(comment.comment_created_by_user, user)

    def test_comment_file_relationship_configuration(self):
        rel = FileComment.__mapper__.relationships["comment_file"]

        self.assertEqual(rel.key, "comment_file")
        self.assertEqual(rel.mapper.class_.__name__, "File")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.back_populates, "file_comments")
        self.assertEqual(rel.lazy, "selectin")
        self.assertTrue(rel.passive_deletes)

    def test_comment_file_primaryjoin(self):
        rel = FileComment.__mapper__.relationships["comment_file"]

        join = str(rel.primaryjoin)

        self.assertIn("files_comments.file_id", join)
        self.assertIn("files.id", join)

    def test_comment_file_target_model(self):
        rel = FileComment.__mapper__.relationships["comment_file"]

        self.assertEqual(rel.mapper.class_, File)

    def test_comment_created_by_user_relationship_configuration(self):
        rel = FileComment.__mapper__.relationships[
            "comment_created_by_user"
        ]

        self.assertEqual(rel.key, "comment_created_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_comment_created_by_user_primaryjoin(self):
        rel = FileComment.__mapper__.relationships[
            "comment_created_by_user"
        ]

        join = str(rel.primaryjoin)

        self.assertIn("files_comments.created_by", join)
        self.assertIn("users.id", join)

    def test_comment_created_by_user_target_model(self):
        rel = FileComment.__mapper__.relationships[
            "comment_created_by_user"
        ]

        self.assertEqual(rel.mapper.class_, User)

    def test_comment_created_by_user_has_no_back_populates(self):
        rel = FileComment.__mapper__.relationships[
            "comment_created_by_user"
        ]

        self.assertIsNone(rel.back_populates)

    def test_sqlite_autoincrement(self):
        self.assertTrue(
            FileComment.__table__.dialect_options["sqlite"]
        )
        self.assertTrue(
            FileComment.__table__.dialect_options["sqlite"][
                "autoincrement"
            ]
        )
