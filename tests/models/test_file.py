# tests/models/test_file.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.schema import CheckConstraint

from app.models.user import User
from app.models.folder import Folder
from app.models.file import File, FileType
from app.models.file_revision import FileRevision  # noqa: F401
from app.models.file_comment import FileComment  # noqa: F401
from app.models.file_tag import FileTag  # noqa: F401
from app.models.file_thumbnail import FileThumbnail  # noqa: F401


class TestFileModel(unittest.TestCase):

    def test_get_relative_path_nested_file(self):
        root = Folder(id=1, dirname="docs", created_by=1)
        api = Folder(id=2, parent_id=1, dirname="api", created_by=1)

        file = File(
            filename="openapi.yaml",
            created_by=1,
            checksum="a" * 64,
        )

        self.assertEqual(
            file.get_relative_path(api, (root,)),
            "docs/api/openapi.yaml",
        )

    def test_get_absolute_path_root_folder_file(self):
        root = Folder(id=1, parent_id=None, dirname="docs", created_by=1)
        file = File(filename="file.txt", created_by=1, checksum="a" * 64)

        config = MagicMock()
        config.FILES_DIR = "/var/lib/hidden/mountpoint/files"

        with patch("app.models.file.get_config", return_value=config):
            self.assertEqual(
                file.get_absolute_path(root, ()),
                "/var/lib/hidden/mountpoint/files/docs/file.txt",
            )

    def test_get_absolute_path_nested_file(self):
        root = Folder(id=1, dirname="docs", created_by=1)
        api = Folder(id=2, parent_id=1, dirname="api", created_by=1)

        file = File(
            filename="openapi.yaml",
            created_by=1,
            checksum="a" * 64,
        )

        config = MagicMock()
        config.FILES_DIR = "/var/lib/hidden/mountpoint/files"

        with patch(
            "app.models.file.get_config",
            return_value=config,
        ):
            self.assertEqual(
                file.get_absolute_path(api, (root,)),
                "/var/lib/hidden/mountpoint/files/docs/api/openapi.yaml",
            )

    def test_relationship_folder_and_files(self):
        folder = Folder(id=1, dirname="docs", created_by=1)
        file = File(
            id=1,
            filename="file.txt",
            created_by=1,
            checksum="a" * 64,
        )

        file.file_folder = folder

        self.assertIs(file.file_folder, folder)
        self.assertIn(file, folder.folder_files)

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

    def test_file_table_name(self):
        self.assertEqual(File.__tablename__, "files")

    def test_folder_id_column_configuration(self):
        column = File.__table__.columns["folder_id"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "folders.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_created_by_column_configuration(self):
        column = File.__table__.columns["created_by"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_updated_by_column_configuration(self):
        column = File.__table__.columns["updated_by"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_filename_column_is_required(self):
        column = File.__table__.columns["filename"]

        self.assertFalse(column.nullable)

    def test_checksum_column_is_required(self):
        column = File.__table__.columns["checksum"]

        self.assertFalse(column.nullable)

    def test_comments_count_column_configuration(self):
        column = File.__table__.columns["comments_count"]

        self.assertFalse(column.nullable)
        self.assertEqual(str(column.type), "INTEGER")
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_file_table_has_comments_count_non_negative_constraint(self):
        constraints = {
            constraint.name
            for constraint in File.__table__.constraints
            if getattr(constraint, "name", None)
        }

        self.assertIn(
            "ck_files_comments_count_non_negative",
            constraints,
        )

    def test_file_comments_count_check_constraint_sqltext(self):
        constraint = next(
            c
            for c in File.__table__.constraints
            if getattr(c, "name", None)
            == "ck_files_comments_count_non_negative"
        )

        self.assertIn(
            "comments_count >= 0",
            str(constraint.sqltext),
        )

    def test_latest_revision_number_column_configuration(self):
        column = File.__table__.columns["latest_revision_number"]

        self.assertFalse(column.nullable)
        self.assertEqual(str(column.type), "INTEGER")
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_file_table_has_latest_revision_number_non_negative_constraint(
        self,
    ):
        constraints = {
            constraint.name
            for constraint in File.__table__.constraints
            if getattr(constraint, "name", None)
        }

        self.assertIn(
            "ck_files_latest_revision_number_non_negative",
            constraints,
        )

    def test_file_latest_revision_number_check_constraint_sqltext(self):
        constraint = next(
            c
            for c in File.__table__.constraints
            if getattr(c, "name", None)
            == "ck_files_latest_revision_number_non_negative"
        )

        self.assertIsInstance(constraint, CheckConstraint)
        self.assertIn(
            "latest_revision_number >= 0",
            str(constraint.sqltext),
        )

    def test_file_table_check_constraints_non_negative_columns(self):
        checks = {
            c.name: c
            for c in File.__table__.constraints
            if isinstance(c, CheckConstraint)
        }

        self.assertEqual(
            set(checks),
            {
                "ck_files_filesize_non_negative",
                "ck_files_comments_count_non_negative",
                "ck_files_latest_revision_number_non_negative",
            },
        )
        self.assertIn(
            "filesize >= 0",
            str(checks["ck_files_filesize_non_negative"].sqltext)
        )
        self.assertIn(
            "comments_count >= 0",
            str(checks["ck_files_comments_count_non_negative"].sqltext),
        )
        self.assertIn(
            "latest_revision_number >= 0",
            str(
                checks[
                    "ck_files_latest_revision_number_non_negative"
                ].sqltext
            ),
        )

    def test_file_table_has_unique_constraint(self):
        constraints = {
            constraint.name
            for constraint in File.__table__.constraints
            if getattr(constraint, "name", None)
        }
        self.assertIn("uq_file_folder_filename", constraints)

    def test_file_unique_constraint_columns(self):
        constraint = next(
            c
            for c in File.__table__.constraints
            if getattr(c, "name", None) == "uq_file_folder_filename"
        )
        column_keys = [col.key for col in constraint.columns]

        self.assertEqual(column_keys, ["folder_id", "filename"])

    def test_file_table_has_sqlite_autoincrement(self):
        self.assertTrue(File.__table__.dialect_options["sqlite"])
        self.assertTrue(
            File.__table__.dialect_options["sqlite"]["autoincrement"]
        )

    def test_file_folder_relationship_configuration(self):
        rel = File.__mapper__.relationships["file_folder"]

        self.assertEqual(rel.key, "file_folder")
        self.assertEqual(rel.mapper.class_.__name__, "Folder")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.back_populates, "folder_files")
        self.assertEqual(rel.lazy, "selectin")

    def test_file_folder_primaryjoin(self):
        rel = File.__mapper__.relationships["file_folder"]

        join = str(rel.primaryjoin)

        self.assertIn("files.folder_id", join)
        self.assertIn("folders.id", join)

    def test_file_folder_target_model(self):
        rel = File.__mapper__.relationships["file_folder"]

        self.assertEqual(rel.mapper.class_, Folder)

    def test_file_created_by_user_relationship_configuration(self):
        rel = File.__mapper__.relationships["file_created_by_user"]

        self.assertEqual(rel.key, "file_created_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_file_created_by_user_primaryjoin(self):
        rel = File.__mapper__.relationships["file_created_by_user"]

        join = str(rel.primaryjoin)

        self.assertIn("files.created_by", join)
        self.assertIn("users.id", join)

    def test_file_created_by_user_target_model(self):
        rel = File.__mapper__.relationships["file_created_by_user"]

        self.assertEqual(rel.mapper.class_, User)

    def test_file_created_by_user_has_no_back_populates(self):
        rel = File.__mapper__.relationships["file_created_by_user"]

        self.assertIsNone(rel.back_populates)

    def test_file_updated_by_user_relationship_configuration(self):
        rel = File.__mapper__.relationships["file_updated_by_user"]

        self.assertEqual(rel.key, "file_updated_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_file_updated_by_user_primaryjoin(self):
        rel = File.__mapper__.relationships["file_updated_by_user"]

        join = str(rel.primaryjoin)

        self.assertIn("files.updated_by", join)
        self.assertIn("users.id", join)

    def test_file_updated_by_user_target_model(self):
        rel = File.__mapper__.relationships["file_updated_by_user"]

        self.assertEqual(rel.mapper.class_, User)

    def test_file_updated_by_user_has_no_back_populates(self):
        rel = File.__mapper__.relationships["file_updated_by_user"]

        self.assertIsNone(rel.back_populates)

    def test_file_revisions_relationship_configuration(self):
        rel = File.__mapper__.relationships["file_revisions"]

        self.assertEqual(rel.key, "file_revisions")
        self.assertEqual(rel.mapper.class_.__name__, "FileRevision")
        self.assertTrue(rel.uselist)
        self.assertEqual(rel.back_populates, "revision_file")

    def test_file_revisions_primaryjoin(self):
        rel = File.__mapper__.relationships["file_revisions"]

        join = str(rel.primaryjoin)

        self.assertIn("files.id", join)
        self.assertIn("files_revisions.file_id", join)

    def test_file_revisions_target_model(self):
        rel = File.__mapper__.relationships["file_revisions"]

        self.assertEqual(rel.mapper.class_, FileRevision)

    def test_file_revisions_order_by_revision_number_desc(self):
        rel = File.__mapper__.relationships["file_revisions"]

        order_by = [str(expr) for expr in rel.order_by]

        self.assertEqual(len(order_by), 1)
        self.assertIn("files_revisions.revision_number", order_by[0])
        self.assertIn("DESC", order_by[0].upper())

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

    def test_file_comments_relationship_configuration(self):
        rel = File.__mapper__.relationships["file_comments"]

        self.assertEqual(rel.key, "file_comments")
        self.assertEqual(rel.mapper.class_.__name__, "FileComment")
        self.assertTrue(rel.uselist)
        self.assertEqual(rel.back_populates, "comment_file")
        self.assertTrue(rel.passive_deletes)

    def test_file_comments_primaryjoin(self):
        rel = File.__mapper__.relationships["file_comments"]

        join = str(rel.primaryjoin)

        self.assertIn("files.id", join)
        self.assertIn("files_comments.file_id", join)

    def test_file_comments_target_model(self):
        rel = File.__mapper__.relationships["file_comments"]

        self.assertEqual(rel.mapper.class_, FileComment)

    def test_file_comments_order_by_created_at_asc(self):
        rel = File.__mapper__.relationships["file_comments"]

        order_by = [str(expr) for expr in rel.order_by]

        self.assertEqual(len(order_by), 1)
        self.assertIn("files_comments.created_at", order_by[0])
        self.assertIn("ASC", order_by[0].upper())

    def test_relationship_file_and_tags(self):
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

    def test_file_tags_relationship_configuration(self):
        rel = File.__mapper__.relationships["file_tags"]

        self.assertEqual(rel.key, "file_tags")
        self.assertEqual(rel.mapper.class_.__name__, "FileTag")
        self.assertTrue(rel.uselist)
        self.assertEqual(rel.back_populates, "tag_file")
        self.assertTrue(rel.passive_deletes)

    def test_file_tags_primaryjoin(self):
        rel = File.__mapper__.relationships["file_tags"]

        join = str(rel.primaryjoin)

        self.assertIn("files.id", join)
        self.assertIn("files_tags.file_id", join)

    def test_file_tags_target_model(self):
        rel = File.__mapper__.relationships["file_tags"]

        self.assertEqual(rel.mapper.class_, FileTag)

    def test_file_tags_order_by_tag_asc(self):
        rel = File.__mapper__.relationships["file_tags"]

        order_by = [str(expr) for expr in rel.order_by]

        self.assertEqual(len(order_by), 1)
        self.assertIn("files_tags.tag", order_by[0])
        self.assertIn("ASC", order_by[0].upper())

    def test_relationship_file_and_thumbnail(self):
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
        )

        thumbnail.thumbnail_file = file

        self.assertIs(thumbnail.thumbnail_file, file)
        self.assertIs(file.file_thumbnail, thumbnail)

    def test_has_thumbnail_true_when_thumbnail_linked(self):
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
        )
        thumbnail.thumbnail_file = file

        self.assertTrue(file.has_thumbnail)

    def test_has_thumbnail_false_when_no_thumbnail(self):
        file = File(
            id=1,
            filename="file.txt",
            created_by=1,
            checksum="a" * 64,
        )
        file.file_thumbnail = None

        self.assertFalse(file.has_thumbnail)

    def test_file_thumbnail_relationship_configuration(self):
        rel = File.__mapper__.relationships["file_thumbnail"]

        self.assertEqual(rel.key, "file_thumbnail")
        self.assertEqual(rel.mapper.class_.__name__, "FileThumbnail")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.back_populates, "thumbnail_file")
        self.assertEqual(rel.lazy, "selectin")

    def test_file_thumbnail_primaryjoin(self):
        rel = File.__mapper__.relationships["file_thumbnail"]

        join = str(rel.primaryjoin)

        self.assertIn("files.id", join)
        self.assertIn("files_thumbnails.file_id", join)

    def test_file_thumbnail_target_model(self):
        rel = File.__mapper__.relationships["file_thumbnail"]

        self.assertEqual(rel.mapper.class_, FileThumbnail)

    def test_is_image_true_for_supported_image_mimetype(self):
        file = File(
            filename="x.png",
            created_by=1,
            checksum="a" * 64,
            mimetype="image/png",
        )
        self.assertTrue(file.is_image)

    def test_is_image_false_for_non_image_mimetype(self):
        file = File(
            filename="x.bin",
            created_by=1,
            checksum="a" * 64,
            mimetype="application/octet-stream",
        )
        self.assertFalse(file.is_image)

    def test_is_image_false_when_mimetype_none(self):
        file = File(
            filename="x",
            created_by=1,
            checksum="a" * 64,
            mimetype=None,
        )
        self.assertFalse(file.is_image)

    def test_is_text_true_for_text_plain(self):
        file = File(
            filename="x.txt",
            created_by=1,
            checksum="a" * 64,
            mimetype="text/plain",
        )
        self.assertTrue(file.is_text)

    def test_is_text_true_for_json_application_type(self):
        file = File(
            filename="x.json",
            created_by=1,
            checksum="a" * 64,
            mimetype="application/json",
        )
        self.assertTrue(file.is_text)

    def test_is_text_false_for_image_mimetype(self):
        file = File(
            filename="x.png",
            created_by=1,
            checksum="a" * 64,
            mimetype="image/png",
        )
        self.assertFalse(file.is_text)

    def test_is_text_false_when_mimetype_none(self):
        file = File(
            filename="x",
            created_by=1,
            checksum="a" * 64,
            mimetype=None,
        )
        self.assertFalse(file.is_text)

    def test_filetype_image_for_supported_image_mimetype(self):
        file = File(
            filename="x.png",
            created_by=1,
            checksum="a" * 64,
            mimetype="image/png",
        )
        self.assertEqual(file.filetype, FileType.IMAGE)

    def test_filetype_text_for_text_plain(self):
        file = File(
            filename="x.txt",
            created_by=1,
            checksum="a" * 64,
            mimetype="text/plain",
        )
        self.assertEqual(file.filetype, FileType.TEXT)

    def test_filetype_text_for_application_json(self):
        file = File(
            filename="x.json",
            created_by=1,
            checksum="a" * 64,
            mimetype="application/json",
        )
        self.assertEqual(file.filetype, FileType.TEXT)

    def test_filetype_binary_for_non_image_non_text_mimetype(self):
        file = File(
            filename="x.bin",
            created_by=1,
            checksum="a" * 64,
            mimetype="application/octet-stream",
        )
        self.assertEqual(file.filetype, FileType.BINARY)

    def test_filetype_binary_when_mimetype_none(self):
        file = File(
            filename="x",
            created_by=1,
            checksum="a" * 64,
            mimetype=None,
        )
        self.assertEqual(file.filetype, FileType.BINARY)
