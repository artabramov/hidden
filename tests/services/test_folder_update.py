# tests/services/test_folder_update.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.exc import IntegrityError

from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.locks import LockType
from app.models.folder import Folder
from app.models.file import File  # noqa: F401
from app.models.file_comment import FileComment  # noqa: F401
from app.models.file_revision import FileRevision  # noqa: F401
from app.models.file_tag import FileTag  # noqa: F401
from app.models.file_thumbnail import FileThumbnail  # noqa: F401
from app.models.user import User
from app.services.folder_update import update_folder


class TestUpdateFolder(unittest.IsolatedAsyncioTestCase):

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_data(self):
        data = MagicMock()
        data.dirname = "new-documents"
        data.summary = "New folder summary"
        data.model_fields_set = {"dirname", "summary"}
        return data

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_folder(self, folder_id, dirname, parent_id=None):
        folder = Folder(
            parent_id=parent_id,
            folder_parent=None,
            created_by=10,
            dirname=dirname,
            summary="Old folder summary",
        )
        folder.id = folder_id
        folder.is_write_protected = False
        return folder

    async def test_raises_not_found_when_folder_missing(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceNotFoundError):
                await update_folder(session, user, 42, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_folder_write_protect(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")
        folder.is_write_protected = True

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceLockedError):
                await update_folder(session, user, 42, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_updates_root_folder_renames_directory_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            result = await update_folder(session, user, 42, data)

        self.assertIs(result, folder)
        self.assertEqual(folder.dirname, "new-documents")
        self.assertEqual(folder.summary, "New folder summary")
        self.assertEqual(folder.updated_by, 10)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files",
            LockType.WRITE,
        )

        repository.update.assert_awaited_once_with(folder)
        rename_mock.assert_awaited_once_with(
            "/mnt/files/documents",
            "/mnt/files/new-documents",
        )

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FOLDER_UPDATE_COMPLETED,
            resource_type=Folder.__tablename__,
            resource_id=folder.id,
        )

        repository.rollback.assert_not_awaited()
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.FOLDER_UPDATE_COMPLETED,
            session,
            folder,
        )

    async def test_updates_child_folder_locks_parent_directory(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_folder(1, "parent")
        folder = self._build_folder(42, "documents", parent_id=parent.id)
        parent_chain = (parent,)

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = parent_chain

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await update_folder(session, user, 42, data)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )

        rename_mock.assert_awaited_once_with(
            "/mnt/files/parent/documents",
            "/mnt/files/parent/new-documents",
        )

    async def test_preserves_summary_when_summary_not_provided(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.summary = "Ignored summary"
        data.model_fields_set = {"dirname"}

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await update_folder(session, user, 42, data)

        self.assertEqual(folder.dirname, "new-documents")
        self.assertEqual(folder.summary, "Old folder summary")

    async def test_clears_summary_when_summary_provided_as_none(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.summary = None
        data.model_fields_set = {"dirname", "summary"}

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await update_folder(session, user, 42, data)

        self.assertIsNone(folder.summary)

    async def test_does_not_rename_directory_when_dirname_unchanged(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.dirname = "documents"

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await update_folder(session, user, 42, data)

        repository.update.assert_awaited_once_with(folder)
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once()

    async def test_rolls_back_and_raises_conflict_on_update_integrity_error(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()
        repository.update.side_effect = IntegrityError(None, None, None)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await update_folder(session, user, 42, data)

        repository.update.assert_awaited_once_with(folder)
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_new_path_too_long(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.dirname = "new"

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_update.FILES_MAX_PATH_LENGTH_BYTES",
                1,
            ),
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await update_folder(session, user, 42, data)

        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_without_cleanup_when_rename_fails(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        error = RuntimeError("rename failed")

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(side_effect=error),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await update_folder(session, user, 42, data)

        self.assertIs(cm.exception, error)

        repository.update.assert_awaited_once_with(folder)
        rename_mock.assert_awaited_once_with(
            "/mnt/files/documents",
            "/mnt/files/new-documents",
        )

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_reverts_directory_when_audit_fails_after_rename(  # noqa: E501
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        error = RuntimeError("audit failed")

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(side_effect=error),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await update_folder(session, user, 42, data)

        self.assertIs(cm.exception, error)

        repository.update.assert_awaited_once_with(folder)
        self.assertEqual(rename_mock.await_count, 2)
        rename_mock.assert_any_await(
            "/mnt/files/documents",
            "/mnt/files/new-documents",
        )
        rename_mock.assert_any_await(
            "/mnt/files/new-documents",
            "/mnt/files/documents",
        )
        write_audit_mock.assert_awaited_once()

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_preserves_original_error_when_directory_revert_fails(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        original_error = RuntimeError("audit failed")
        revert_error = RuntimeError("revert failed")

        rename_mock = AsyncMock(
            side_effect=[None, revert_error],
        )

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=rename_mock,
            ),
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(side_effect=original_error),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await update_folder(session, user, 42, data)

        self.assertIs(cm.exception, original_error)

        repository.update.assert_awaited_once_with(folder)
        self.assertEqual(rename_mock.await_count, 2)
        write_audit_mock.assert_awaited_once()

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_does_not_rollback_or_revert_when_hook_fails_after_commit(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        error = RuntimeError("hook failed")

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(side_effect=error),
            ) as emit_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await update_folder(session, user, 42, data)

        self.assertIs(cm.exception, error)

        repository.update.assert_awaited_once_with(folder)
        rename_mock.assert_awaited_once_with(
            "/mnt/files/documents",
            "/mnt/files/new-documents",
        )
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()

        repository.rollback.assert_not_awaited()
        emit_mock.assert_awaited_once_with(
            E.FOLDER_UPDATE_COMPLETED,
            session,
            folder,
        )

    async def test_raises_conflict_when_filesystem_directory_exists(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir_mock,
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await update_folder(session, user, 42, data)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files",
            LockType.WRITE,
        )

        isdir_mock.assert_awaited_once_with("/mnt/files/new-documents")
        isfile_mock.assert_not_awaited()

        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_filesystem_file_exists(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder(42, "documents")

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_update.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_update.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_update.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir_mock,
            patch(
                "app.services.folder_update.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.folder_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.folder_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await update_folder(session, user, 42, data)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files",
            LockType.WRITE,
        )

        isdir_mock.assert_awaited_once_with("/mnt/files/new-documents")
        isfile_mock.assert_awaited_once_with("/mnt/files/new-documents")

        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
