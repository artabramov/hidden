# tests/models/test_folder.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.schema import CheckConstraint

from app.models.folder import Folder
from app.models.file import File  # noqa: F401
from app.models.file_comment import FileComment  # noqa: F401
from app.models.file_revision import FileRevision  # noqa: F401
from app.models.file_tag import FileTag  # noqa: F401
from app.models.file_thumbnail import FileThumbnail  # noqa: F401
from app.models.user import User


class TestFolderModel(unittest.TestCase):

    def test_relationship_parent_and_children(self):
        root = Folder(id=1, dirname="root", created_by=1)
        child = Folder(id=2, dirname="child", created_by=1)

        child.folder_parent = root

        self.assertIs(child.folder_parent, root)
        self.assertIn(child, root.folder_children)

    def test_folder_table_name(self):
        self.assertEqual(Folder.__tablename__, "folders")

    def test_folder_table_has_unique_index(self):
        index_names = {index.name for index in Folder.__table__.indexes}
        self.assertIn("uq_folders_parent_id_dirname", index_names)

    def test_folder_table_has_sqlite_autoincrement(self):
        self.assertTrue(Folder.__table__.dialect_options["sqlite"])
        self.assertTrue(
            Folder.__table__.dialect_options["sqlite"]["autoincrement"]
        )

    def test_folder_parent_relationship_configuration(self):
        rel = Folder.__mapper__.relationships["folder_parent"]

        self.assertEqual(rel.key, "folder_parent")
        self.assertEqual(rel.mapper.class_.__name__, "Folder")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.back_populates, "folder_children")
        self.assertEqual(rel.lazy, "selectin")

    def test_folder_parent_relationship_has_remote_side(self):
        rel = Folder.__mapper__.relationships["folder_parent"]

        remote_side_columns = {column.name for column in rel.remote_side}

        self.assertEqual(remote_side_columns, {"id"})

    def test_folder_children_relationship_configuration(self):
        rel = Folder.__mapper__.relationships["folder_children"]

        self.assertEqual(rel.key, "folder_children")
        self.assertEqual(rel.mapper.class_.__name__, "Folder")
        self.assertTrue(rel.uselist)
        self.assertEqual(rel.back_populates, "folder_parent")
        self.assertEqual(rel.lazy, "selectin")

    def test_folder_children_primaryjoin(self):
        rel = Folder.__mapper__.relationships["folder_children"]

        join = str(rel.primaryjoin)

        self.assertIn("folders.id", join)
        self.assertIn("folders.parent_id", join)

    def test_folder_files_relationship_configuration(self):
        rel = Folder.__mapper__.relationships["folder_files"]

        self.assertEqual(rel.key, "folder_files")
        self.assertEqual(rel.mapper.class_.__name__, "File")
        self.assertTrue(rel.uselist)
        self.assertEqual(rel.back_populates, "file_folder")
        self.assertEqual(rel.lazy, "selectin")

    def test_folder_files_primaryjoin(self):
        rel = Folder.__mapper__.relationships["folder_files"]

        join = str(rel.primaryjoin)

        self.assertIn("folders.id", join)
        self.assertIn("files.folder_id", join)

    def test_folder_files_is_one_to_many(self):
        rel = Folder.__mapper__.relationships["folder_files"]

        self.assertTrue(rel.uselist)

    def test_folder_files_target_model(self):
        rel = Folder.__mapper__.relationships["folder_files"]

        self.assertEqual(rel.mapper.class_.__name__, "File")

    def test_folder_files_back_populates(self):
        rel = Folder.__mapper__.relationships["folder_files"]

        self.assertEqual(rel.back_populates, "file_folder")

    def test_folder_created_by_user_relationship_configuration(self):
        rel = Folder.__mapper__.relationships["folder_created_by_user"]

        self.assertEqual(rel.key, "folder_created_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_folder_created_by_user_primaryjoin(self):
        rel = Folder.__mapper__.relationships["folder_created_by_user"]

        join = str(rel.primaryjoin)

        self.assertIn("folders.created_by", join)
        self.assertIn("users.id", join)

    def test_folder_created_by_user_target_model(self):
        rel = Folder.__mapper__.relationships["folder_created_by_user"]

        self.assertEqual(rel.mapper.class_, User)

    def test_folder_created_by_user_has_no_back_populates(self):
        rel = Folder.__mapper__.relationships["folder_created_by_user"]

        self.assertIsNone(rel.back_populates)

    def test_folder_created_by_user_lazy_strategy(self):
        rel = Folder.__mapper__.relationships["folder_created_by_user"]

        self.assertEqual(rel.lazy, "selectin")

    def test_folder_updated_by_user_relationship_configuration(self):
        rel = Folder.__mapper__.relationships["folder_updated_by_user"]

        self.assertEqual(rel.key, "folder_updated_by_user")
        self.assertEqual(rel.mapper.class_.__name__, "User")
        self.assertFalse(rel.uselist)
        self.assertEqual(rel.lazy, "selectin")

    def test_folder_updated_by_user_primaryjoin(self):
        rel = Folder.__mapper__.relationships["folder_updated_by_user"]

        join = str(rel.primaryjoin)

        self.assertIn("folders.updated_by", join)
        self.assertIn("users.id", join)

    def test_folder_updated_by_user_target_model(self):
        rel = Folder.__mapper__.relationships["folder_updated_by_user"]

        self.assertEqual(rel.mapper.class_, User)

    def test_folder_updated_by_user_has_no_back_populates(self):
        rel = Folder.__mapper__.relationships["folder_updated_by_user"]

        self.assertIsNone(rel.back_populates)

    def test_folder_updated_by_user_lazy_strategy(self):
        rel = Folder.__mapper__.relationships["folder_updated_by_user"]

        self.assertEqual(rel.lazy, "selectin")

    def test_folder_unique_index_uses_coalesce_for_root(self):
        indexes = {
            index.name: index
            for index in Folder.__table__.indexes
        }

        index = indexes["uq_folders_parent_id_dirname"]
        expressions = [str(expr) for expr in index.expressions]

        self.assertEqual(len(expressions), 2)
        self.assertIn("coalesce", expressions[0].lower())
        self.assertIn("folders.parent_id", expressions[0])
        self.assertIn(":param", expressions[0])
        self.assertIn("folders.dirname", expressions[1])

    def test_created_by_column_configuration(self):
        column = Folder.__table__.columns["created_by"]

        self.assertFalse(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_updated_by_column_configuration(self):
        column = Folder.__table__.columns["updated_by"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "users.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_parent_id_column_allows_null_for_root_folder(self):
        column = Folder.__table__.columns["parent_id"]

        self.assertTrue(column.nullable)
        self.assertTrue(column.index)
        self.assertEqual(len(column.foreign_keys), 1)

        fk = next(iter(column.foreign_keys))
        self.assertEqual(fk.target_fullname, "folders.id")
        self.assertEqual(fk.ondelete, "RESTRICT")

    def test_dirname_column_is_required(self):
        column = Folder.__table__.columns["dirname"]

        self.assertFalse(column.nullable)

    def test_children_count_column_configuration(self):
        column = Folder.__table__.columns["children_count"]

        self.assertFalse(column.nullable)
        self.assertEqual(str(column.type), "INTEGER")
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_files_count_column_configuration(self):
        column = Folder.__table__.columns["files_count"]

        self.assertFalse(column.nullable)
        self.assertEqual(str(column.type), "INTEGER")
        self.assertIsNotNone(column.server_default)
        self.assertEqual(str(column.server_default.arg), "0")

    def test_folder_table_has_children_count_non_negative_constraint(self):
        constraints = {
            constraint.name
            for constraint in Folder.__table__.constraints
            if getattr(constraint, "name", None)
        }

        self.assertIn(
            "ck_folders_children_count_non_negative",
            constraints,
        )

    def test_folder_children_count_check_constraint_sqltext(self):
        constraint = next(
            c
            for c in Folder.__table__.constraints
            if getattr(c, "name", None)
            == "ck_folders_children_count_non_negative"
        )

        self.assertIsInstance(constraint, CheckConstraint)
        self.assertIn(
            "children_count >= 0",
            str(constraint.sqltext),
        )

    def test_folder_table_has_files_count_non_negative_constraint(self):
        constraints = {
            constraint.name
            for constraint in Folder.__table__.constraints
            if getattr(constraint, "name", None)
        }

        self.assertIn(
            "ck_folders_files_count_non_negative",
            constraints,
        )

    def test_folder_files_count_check_constraint_sqltext(self):
        constraint = next(
            c
            for c in Folder.__table__.constraints
            if getattr(c, "name", None)
            == "ck_folders_files_count_non_negative"
        )

        self.assertIsInstance(constraint, CheckConstraint)
        self.assertIn(
            "files_count >= 0",
            str(constraint.sqltext),
        )

    def test_folder_table_check_constraints_only_child_count_non_negative(
        self,
    ):
        checks = {
            c.name: c
            for c in Folder.__table__.constraints
            if isinstance(c, CheckConstraint)
        }

        self.assertEqual(
            set(checks),
            {
                "ck_folders_children_count_non_negative",
                "ck_folders_files_count_non_negative",
            },
        )
        self.assertIn(
            "children_count >= 0",
            str(checks["ck_folders_children_count_non_negative"].sqltext),
        )
        self.assertIn(
            "files_count >= 0",
            str(checks["ck_folders_files_count_non_negative"].sqltext),
        )

    # --- _get_relative_dir ---

    def test_get_relative_dir_returns_dirname_for_root_parent_chain(self):
        folder = Folder(id=1, dirname="root", created_by=1)

        self.assertEqual(
            folder._get_relative_dir(parent_chain=()),
            "root",
        )

    def test_parent_chain_required_when_folder_has_parent_id(self):
        folder = Folder(
            id=2,
            parent_id=1,
            dirname="child",
            created_by=1,
        )

        with self.assertRaises(ValueError) as cm:
            folder._get_relative_dir(parent_chain=())

        self.assertEqual(
            str(cm.exception),
            "Parent chain is required",
        )

    def test_get_relative_dir_joins_parent_chain_from_root_to_folder(self):
        root = Folder(id=1, dirname="root", created_by=1)
        parent = Folder(
            id=2,
            parent_id=1,
            dirname="parent",
            created_by=1,
        )
        folder = Folder(
            id=3,
            parent_id=2,
            dirname="child",
            created_by=1,
        )

        self.assertEqual(
            folder._get_relative_dir(parent_chain=(parent, root)),
            "root/parent/child",
        )

    # --- get_absolute_dir ---

    def test_get_absolute_dir_joins_files_dir_and_relative_dir(self):
        root = Folder(id=1, dirname="root", created_by=1)
        parent = Folder(
            id=2,
            parent_id=1,
            dirname="parent",
            created_by=1,
        )
        folder = Folder(
            id=3,
            parent_id=2,
            dirname="child",
            created_by=1,
        )

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with patch("app.models.folder.get_config", return_value=config):
            self.assertEqual(
                folder.get_absolute_dir(parent_chain=(parent, root)),
                "/mnt/files/root/parent/child",
            )

    # --- is_write_protected_recursive ---

    def test_is_write_protected_recursive_false_when_unprotected(self):
        root = Folder(id=1, dirname="root", created_by=1)
        folder = Folder(
            id=2,
            parent_id=1,
            dirname="child",
            created_by=1,
            is_write_protected=False,
        )

        self.assertFalse(
            folder.is_write_protected_recursive(parent_chain=(root,)),
        )

    def test_is_write_protected_recursive_false_when_only_self_protected(self):
        root = Folder(id=1, dirname="root", created_by=1)
        folder = Folder(
            id=2,
            parent_id=1,
            dirname="child",
            created_by=1,
            is_write_protected=True,
        )

        self.assertFalse(
            folder.is_write_protected_recursive(parent_chain=(root,)),
        )

    def test_is_write_protected_recursive_true_when_ancestor_protected(self):
        root = Folder(
            id=1,
            dirname="root",
            created_by=1,
            is_write_protected=True,
        )
        folder = Folder(
            id=2,
            parent_id=1,
            dirname="child",
            created_by=1,
            is_write_protected=False,
        )

        self.assertTrue(
            folder.is_write_protected_recursive(parent_chain=(root,)),
        )

    # --- _validate_parent_chain ---

    def test_parent_chain_rejects_wrong_direct_parent(self):
        wrong_parent = Folder(id=99, dirname="wrong", created_by=1)
        folder = Folder(
            id=3,
            parent_id=2,
            dirname="child",
            created_by=1,
        )

        with self.assertRaises(ValueError) as cm:
            folder._get_relative_dir(parent_chain=(wrong_parent,))

        self.assertIn(
            "direct parent",
            str(cm.exception),
        )

    def test_parent_chain_rejects_broken_linkage(self):
        root = Folder(id=1, dirname="root", created_by=1)
        parent = Folder(
            id=2,
            parent_id=99,
            dirname="parent",
            created_by=1,
        )
        folder = Folder(
            id=3,
            parent_id=2,
            dirname="child",
            created_by=1,
        )

        with self.assertRaises(ValueError) as cm:
            folder._get_relative_dir(parent_chain=(parent, root))

        self.assertEqual(
            str(cm.exception),
            "Invalid parent chain linkage",
        )

    def test_parent_chain_rejects_cycle(self):
        parent = Folder(
            id=2,
            parent_id=2,
            dirname="parent",
            created_by=1,
        )
        folder = Folder(
            id=3,
            parent_id=2,
            dirname="child",
            created_by=1,
        )

        with self.assertRaises(ValueError) as cm:
            folder._get_relative_dir(parent_chain=(parent, parent))

        self.assertEqual(
            str(cm.exception),
            "Cycle detected in folder tree",
        )
