# tests/models/test_file_thumbnail.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock, patch

from app.models.file import File  # noqa: F401
from app.models.file_thumbnail import FileThumbnail
from app.models.user import User


class TestFileThumbnailModel(unittest.TestCase):

    def test_absolute_path(self):
        thumbnail = FileThumbnail(
            thumbnail_uuid="550e8400-e29b-41d4-a716-446655440000",
            file_id=1,
            created_by=1,
            filesize=123,
            mimetype="image/webp",
            width=320,
            height=180,
        )

        config = MagicMock()
        config.FILES_THUMBNAILS_DIR = "/var/lib/hidden/mountpoint/thumbnails"

        with patch(
            "app.models.file_thumbnail.get_config",
            return_value=config,
        ):
            self.assertEqual(
                thumbnail.absolute_path,
                "/var/lib/hidden/mountpoint/thumbnails/"
                "550e8400-e29b-41d4-a716-446655440000",
            )

    def test_absolute_path_uses_os_path_join(self):
        thumbnail = FileThumbnail(
            thumbnail_uuid="thumb-uuid-1",
            file_id=1,
            created_by=1,
            filesize=123,
            mimetype="image/webp",
            width=320,
            height=180,
        )

        config = MagicMock()
        config.FILES_THUMBNAILS_DIR = "/base"

        with patch(
            "app.models.file_thumbnail.get_config",
            return_value=config,
        ), patch(
            "app.models.file_thumbnail.os.path.join",
            return_value="/joined/path",
        ) as mock_join:
            out = thumbnail.absolute_path

        self.assertEqual(out, "/joined/path")
        mock_join.assert_called_once_with("/base", "thumb-uuid-1")

    def test_relationship_thumbnail_and_file(self):
        file = File(
            id=1,
            filename="file.txt",
            created_by=1,
            checksum="a" * 64,
        )
        thumbnail = FileThumbnail(
            id=1,
            file_id=1,
            created_by=1,
            thumbnail_uuid="thumb-uuid-1",
            filesize=123,
            mimetype="image/webp",
            width=320,
            height=180,
        )

        thumbnail.thumbnail_file = file

        self.assertIs(thumbnail.thumbnail_file, file)
        self.assertIs(file.file_thumbnail, thumbnail)

    def test_relationship_thumbnail_and_created_by_user(self):
        user = User(
            id=1,
            username="alice",
            password_hash="hash",
            totp_secret_encrypted="secret",
            display_name="Alice",
        )
        thumbnail = FileThumbnail(
            id=1,
            file_id=1,
            created_by=1,
            thumbnail_uuid="thumb-uuid-1",
            filesize=123,
            mimetype="image/webp",
            width=320,
            height=180,
        )

        thumbnail.thumbnail_created_by_user = user

        self.assertIs(thumbnail.thumbnail_created_by_user, user)

    def test_file_thumbnail_table_name(self):
        self.assertEqual(FileThumbnail.__tablename__, "files_thumbnails")

    def test_file_id_column_configuration(self):
        column = FileThumbnail.__table__.columns["file_id"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "files.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_created_by_column_configuration(self):
        column = FileThumbnail.__table__.columns["created_by"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_thumbnail_uuid_column_is_required(self):
        column = FileThumbnail.__table__.columns["thumbnail_uuid"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.unique)

    def test_filesize_column_is_required(self):
        column = FileThumbnail.__table__.columns["filesize"]

        self.assertFalse(column.nullable)

    def test_mimetype_column_is_required(self):
        column = FileThumbnail.__table__.columns["mimetype"]

        self.assertFalse(column.nullable)

    def test_width_column_is_required(self):
        column = FileThumbnail.__table__.columns["width"]

        self.assertFalse(column.nullable)

    def test_height_column_is_required(self):
        column = FileThumbnail.__table__.columns["height"]

        self.assertFalse(column.nullable)

    def test_file_thumbnail_table_has_unique_index(self):
        index_names = {index.name for index in FileThumbnail.__table__.indexes}
        self.assertIn("uq_files_thumbnails_file_id", index_names)

    def test_file_thumbnail_unique_index_uses_file_id(self):
        indexes = {
            index.name: index
            for index in FileThumbnail.__table__.indexes
        }

        index = indexes["uq_files_thumbnails_file_id"]
        expressions = [str(expr) for expr in index.expressions]

        self.assertEqual(len(expressions), 1)
        self.assertIn("files_thumbnails.file_id", expressions[0])

    def test_file_thumbnail_table_has_sqlite_autoincrement(self):
        self.assertTrue(FileThumbnail.__table__.dialect_options["sqlite"])
        self.assertTrue(
            FileThumbnail.__table__.dialect_options["sqlite"]["autoincrement"]
        )

    def test_thumbnail_file_relationship_configuration(self):
        rel = FileThumbnail.__mapper__.relationships["thumbnail_file"]

        self.assertEqual(rel.key, "thumbnail_file")
        self.assertEqual(rel.mapper.class_.__name__, "File")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.back_populates, "file_thumbnail")
        self.assertEqual(rel.lazy, "selectin")

    def test_thumbnail_file_primaryjoin(self):
        rel = FileThumbnail.__mapper__.relationships["thumbnail_file"]

        join = str(rel.primaryjoin)

        self.assertIn("files.id", join)
        self.assertIn("files_thumbnails.file_id", join)

    def test_thumbnail_file_target_model(self):
        rel = FileThumbnail.__mapper__.relationships["thumbnail_file"]

        self.assertEqual(rel.mapper.class_, File)

    def test_thumbnail_created_by_user_relationship_configuration(self):
        rel = FileThumbnail.__mapper__.relationships[
            "thumbnail_created_by_user"
        ]

        self.assertEqual(rel.key, "thumbnail_created_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_thumbnail_created_by_user_primaryjoin(self):
        rel = FileThumbnail.__mapper__.relationships[
            "thumbnail_created_by_user"
        ]

        join = str(rel.primaryjoin)

        self.assertIn("files_thumbnails.created_by", join)
        self.assertIn("users.id", join)

    def test_thumbnail_created_by_user_target_model(self):
        rel = FileThumbnail.__mapper__.relationships[
            "thumbnail_created_by_user"
        ]

        self.assertEqual(rel.mapper.class_, User)

    def test_thumbnail_created_by_user_has_no_back_populates(self):
        rel = FileThumbnail.__mapper__.relationships[
            "thumbnail_created_by_user"
        ]

        self.assertIsNone(rel.back_populates)

    def test_file_thumbnail_table_has_filesize_positive_constraint(self):
        constraints = {
            constraint.name
            for constraint in FileThumbnail.__table__.constraints
            if getattr(constraint, "name", None)
        }

        self.assertIn(
            "ck_files_thumbnails_filesize_positive",
            constraints,
        )

    def test_file_thumbnail_table_has_width_positive_constraint(self):
        constraints = {
            constraint.name
            for constraint in FileThumbnail.__table__.constraints
            if getattr(constraint, "name", None)
        }

        self.assertIn(
            "ck_files_thumbnails_width_positive",
            constraints,
        )

    def test_file_thumbnail_table_has_height_positive_constraint(self):
        constraints = {
            constraint.name
            for constraint in FileThumbnail.__table__.constraints
            if getattr(constraint, "name", None)
        }

        self.assertIn(
            "ck_files_thumbnails_height_positive",
            constraints,
        )
