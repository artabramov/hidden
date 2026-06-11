# tests/models/test_file_revision.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock, patch

from app.models.file import File  # noqa: F401
from app.models.file_revision import FileRevision
from app.models.user import User


class TestFileRevisionModel(unittest.TestCase):

    def test_absolute_path(self):
        revision = FileRevision(
            revision_uuid="550e8400-e29b-41d-a716-446655440000",
            filename="file.txt",
            created_by=1,
            file_id=1,
            checksum="a" * 64,
        )

        config = MagicMock()
        config.FILES_REVISIONS_DIR = "/var/lib/hidden/mountpoint/revisions"

        with patch(
            "app.models.file_revision.get_config",
            return_value=config,
        ):
            self.assertEqual(
                revision.absolute_path,
                "/var/lib/hidden/mountpoint/revisions/"
                "550e8400-e29b-41d-a716-446655440000",
            )

    def test_absolute_path_uses_os_path_join(self):
        revision = FileRevision(
            revision_uuid="rev-uuid-1",
            filename="file.txt",
            created_by=1,
            file_id=1,
            checksum="a" * 64,
        )
        config = MagicMock()
        config.FILES_REVISIONS_DIR = "/base"

        with patch(
            "app.models.file_revision.get_config",
            return_value=config,
        ), patch(
            "app.models.file_revision.os.path.join",
            return_value="/joined/path",
        ) as mock_join:
            out = revision.absolute_path

        self.assertEqual(out, "/joined/path")
        mock_join.assert_called_once_with("/base", "rev-uuid-1")

    def test_relationship_file_and_revisions(self):
        file = File(
            id=1,
            filename="file.txt",
            created_by=1,
            checksum="a" * 64,
        )
        revision = FileRevision(
            id=1,
            file_id=1,
            created_by=1,
            revision_number=1,
            revision_uuid="rev-uuid-1",
            filename="file.txt",
            checksum="b" * 64,
        )

        revision.revision_file = file

        self.assertIs(revision.revision_file, file)
        self.assertIn(revision, file.file_revisions)

    def test_file_revision_table_name(self):
        self.assertEqual(FileRevision.__tablename__, "files_revisions")

    def test_file_id_column_configuration(self):
        column = FileRevision.__table__.columns["file_id"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "files.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_created_by_column_configuration(self):
        column = FileRevision.__table__.columns["created_by"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_revision_number_column_is_required(self):
        column = FileRevision.__table__.columns["revision_number"]

        self.assertFalse(column.nullable)

    def test_revision_uuid_column_is_required(self):
        column = FileRevision.__table__.columns["revision_uuid"]

        self.assertFalse(column.nullable)

    def test_filename_column_is_required(self):
        column = FileRevision.__table__.columns["filename"]

        self.assertFalse(column.nullable)

    def test_checksum_column_is_required(self):
        column = FileRevision.__table__.columns["checksum"]

        self.assertFalse(column.nullable)

    def test_file_revision_table_has_unique_index(self):
        index_names = {
            index.name for index in FileRevision.__table__.indexes
        }
        self.assertIn(
            "uq_files_revisions_file_id_revision_number",
            index_names,
        )

    def test_file_revision_unique_index_columns(self):
        indexes = {
            index.name: index
            for index in FileRevision.__table__.indexes
        }

        index = indexes["uq_files_revisions_file_id_revision_number"]
        expressions = [str(expr) for expr in index.expressions]

        self.assertEqual(len(expressions), 2)
        self.assertIn("files_revisions.file_id", expressions[0])
        self.assertIn("files_revisions.revision_number", expressions[1])

    def test_file_revision_table_has_sqlite_autoincrement(self):
        self.assertTrue(FileRevision.__table__.dialect_options["sqlite"])
        self.assertTrue(
            FileRevision.__table__.dialect_options["sqlite"][
                "autoincrement"
            ]
        )

    def test_revision_file_relationship_configuration(self):
        rel = FileRevision.__mapper__.relationships["revision_file"]

        self.assertEqual(rel.key, "revision_file")
        self.assertEqual(rel.mapper.class_.__name__, "File")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.back_populates, "file_revisions")

    def test_revision_file_primaryjoin(self):
        rel = FileRevision.__mapper__.relationships["revision_file"]

        join = str(rel.primaryjoin)

        self.assertIn("files_revisions.file_id", join)
        self.assertIn("files.id", join)

    def test_revision_file_target_model(self):
        rel = FileRevision.__mapper__.relationships["revision_file"]

        self.assertEqual(rel.mapper.class_, File)

    def test_revision_created_by_user_relationship_configuration(self):
        rel = FileRevision.__mapper__.relationships[
            "revision_created_by_user"
        ]

        self.assertEqual(rel.key, "revision_created_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_revision_created_by_user_primaryjoin(self):
        rel = FileRevision.__mapper__.relationships[
            "revision_created_by_user"
        ]

        join = str(rel.primaryjoin)

        self.assertIn("files_revisions.created_by", join)
        self.assertIn("users.id", join)

    def test_revision_created_by_user_target_model(self):
        rel = FileRevision.__mapper__.relationships[
            "revision_created_by_user"
        ]

        self.assertEqual(rel.mapper.class_, User)

    def test_revision_created_by_user_has_no_back_populates(self):
        rel = FileRevision.__mapper__.relationships[
            "revision_created_by_user"
        ]

        self.assertIsNone(rel.back_populates)
