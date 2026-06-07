# tests/services/test_folder_create.py
# SPDX-License-Identifier: SSPL-1.0

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
from app.services.folder_create import create_folder


class TestCreateFolder(unittest.IsolatedAsyncioTestCase):

    def _build_data(self):
        data = MagicMock()
        data.parent_id = 1
        data.dirname = "documents"
        data.summary = "Folder summary"
        return data

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_parent(self):
        parent = Folder(
            parent_id=None,
            folder_parent=None,
            created_by=10,
            dirname="parent",
            summary="Parent folder",
            children_count=0,
            files_count=0,
        )
        parent.id = 1
        parent.is_write_protected = False
        return parent

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
            summary=None,
            children_count=0,
            files_count=0,
        )
        folder.id = folder_id
        folder.is_write_protected = False
        return folder

    async def test_raises_not_found_when_parent_missing(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceNotFoundError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_not_awaited()
        repository.insert.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        mkdir_mock.assert_not_awaited()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_write_protected(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()
        parent.is_write_protected = True

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceLockedError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        repository.insert.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        mkdir_mock.assert_not_awaited()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_creates_folder_under_parent_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            folder = await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )

        repository.insert.assert_awaited_once()
        insert_args, insert_kwargs = repository.insert.await_args
        created_folder = insert_args[0]

        self.assertIs(folder, created_folder)
        self.assertIsInstance(created_folder, Folder)
        self.assertEqual(insert_kwargs, {})

        self.assertEqual(created_folder.parent_id, 1)
        self.assertIsNone(created_folder.folder_parent)
        self.assertEqual(created_folder.created_by, 10)
        self.assertEqual(created_folder.dirname, "documents")
        self.assertEqual(created_folder.summary, "Folder summary")

        self.assertEqual(parent.children_count, 1)
        repository.update.assert_awaited_once_with(parent)

        mkdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        rmdir_mock.assert_not_awaited()

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FOLDER_CREATE_COMPLETED,
            resource_type=Folder.__tablename__,
            resource_id=created_folder.id,
        )

        repository.rollback.assert_not_awaited()
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.FOLDER_CREATE_COMPLETED,
            session,
            created_folder,
        )

    async def test_increments_parent_children_count_from_existing_value(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()
        parent.children_count = 12

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await create_folder(session, user, data)

        self.assertEqual(parent.children_count, 13)
        repository.update.assert_awaited_once_with(parent)

    async def test_creates_folder_in_root_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.parent_id = None

        repository = AsyncMock()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_create.get_config",
                return_value=config,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            folder = await create_folder(session, user, data)

        repository.select.assert_not_awaited()
        repository.select_parent_chain.assert_not_awaited()

        lock_directory_mock.assert_called_once_with(
            "/mnt/files",
            LockType.WRITE,
        )

        repository.insert.assert_awaited_once()
        insert_args, insert_kwargs = repository.insert.await_args
        created_folder = insert_args[0]

        self.assertIs(folder, created_folder)
        self.assertIsInstance(created_folder, Folder)
        self.assertEqual(insert_kwargs, {})

        repository.update.assert_not_awaited()

        self.assertIsNone(created_folder.parent_id)
        self.assertIsNone(created_folder.folder_parent)
        self.assertEqual(created_folder.created_by, 10)
        self.assertEqual(created_folder.dirname, "documents")
        self.assertEqual(created_folder.summary, "Folder summary")

        mkdir_mock.assert_awaited_once_with("/mnt/files/documents")
        rmdir_mock.assert_not_awaited()

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FOLDER_CREATE_COMPLETED,
            resource_type=Folder.__tablename__,
            resource_id=created_folder.id,
        )

        repository.rollback.assert_not_awaited()
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.FOLDER_CREATE_COMPLETED,
            session,
            created_folder,
        )

    async def test_rolls_back_and_raises_conflict_on_insert_integrity_error(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())
        repository.insert.side_effect = IntegrityError(None, None, None)

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )

        repository.insert.assert_awaited_once()
        repository.update.assert_not_awaited()
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        self.assertEqual(parent.children_count, 0)

        mkdir_mock.assert_not_awaited()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_without_cleanup_when_mkdir_fails(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()
        error = RuntimeError("mkdir failed")

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(side_effect=error),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await create_folder(session, user, data)

        self.assertIs(cm.exception, error)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        repository.insert.assert_awaited_once()
        repository.update.assert_awaited_once_with(parent)
        self.assertEqual(parent.children_count, 1)
        mkdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_cleans_up_when_audit_fails_after_mkdir(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()
        error = RuntimeError("audit failed")

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(side_effect=error),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await create_folder(session, user, data)

        self.assertIs(cm.exception, error)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        repository.insert.assert_awaited_once()
        repository.update.assert_awaited_once_with(parent)
        self.assertEqual(parent.children_count, 1)
        mkdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        write_audit_mock.assert_awaited_once()

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        rmdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_cleans_up_when_commit_fails_after_mkdir(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())
        repository.commit.side_effect = RuntimeError("commit failed")

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        repository.insert.assert_awaited_once()
        repository.update.assert_awaited_once_with(parent)
        self.assertEqual(parent.children_count, 1)
        mkdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()

        repository.rollback.assert_awaited_once()
        rmdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        emit_mock.assert_not_awaited()

    async def test_preserves_original_error_when_cleanup_fails(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()
        original_error = RuntimeError("audit failed")
        cleanup_error = RuntimeError("cleanup failed")

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(side_effect=cleanup_error),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(side_effect=original_error),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await create_folder(session, user, data)

        self.assertIs(cm.exception, original_error)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        repository.insert.assert_awaited_once()
        repository.update.assert_awaited_once_with(parent)
        self.assertEqual(parent.children_count, 1)
        mkdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        write_audit_mock.assert_awaited_once()

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        rmdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        emit_mock.assert_not_awaited()

    async def test_does_not_rollback_or_cleanup_when_hook_fails_after_commit(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()
        error = RuntimeError("hook failed")

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(side_effect=error),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await create_folder(session, user, data)

        self.assertIs(cm.exception, error)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        repository.insert.assert_awaited_once()
        repository.update.assert_awaited_once_with(parent)
        self.assertEqual(parent.children_count, 1)
        mkdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()

        repository.rollback.assert_not_awaited()
        rmdir_mock.assert_not_awaited()

        emit_mock.assert_awaited_once()

    async def test_raises_conflict_when_folder_depth_limit_exceeded(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        root_parent = self._build_folder(1, "root-parent")
        grandparent = self._build_folder(
            2,
            "grandparent",
            parent_id=root_parent.id,
        )
        parent = self._build_folder(
            3,
            "parent",
            parent_id=grandparent.id,
        )
        data.parent_id = parent.id

        parent_chain = (grandparent, root_parent)

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=parent_chain)

        with (
            patch("app.services.folder_create.FILES_MAX_FOLDER_DEPTH", 2),
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=3)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        mkdir_mock.assert_not_awaited()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_allows_folder_create_at_folder_depth_limit(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        grandparent = self._build_folder(2, "grandparent")
        parent = self._build_folder(
            3,
            "parent",
            parent_id=grandparent.id,
        )
        data.parent_id = parent.id

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=(grandparent,))

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch("app.services.folder_create.FILES_MAX_FOLDER_DEPTH", 2),
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            folder = await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=3)
        repository.select_parent_chain.assert_awaited_once_with(parent)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/grandparent/parent",
            LockType.WRITE,
        )

        repository.insert.assert_awaited_once()
        insert_args, insert_kwargs = repository.insert.await_args
        created_folder = insert_args[0]

        self.assertIs(folder, created_folder)
        self.assertIsInstance(created_folder, Folder)
        self.assertEqual(insert_kwargs, {})

        self.assertEqual(created_folder.parent_id, 3)
        self.assertEqual(created_folder.created_by, 10)
        self.assertEqual(created_folder.dirname, "documents")
        self.assertEqual(created_folder.summary, "Folder summary")

        self.assertEqual(parent.children_count, 1)
        repository.update.assert_awaited_once_with(parent)

        mkdir_mock.assert_awaited_once_with(
            "/mnt/files/grandparent/parent/documents",
        )
        rmdir_mock.assert_not_awaited()

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FOLDER_CREATE_COMPLETED,
            resource_type=Folder.__tablename__,
            resource_id=created_folder.id,
        )

        repository.rollback.assert_not_awaited()
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.FOLDER_CREATE_COMPLETED,
            session,
            created_folder,
        )

    async def test_raises_conflict_when_folder_path_too_long(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.FILES_MAX_PATH_LENGTH_BYTES",
                len("/mnt/files/parent/documents".encode("utf-8")) - 1,
            ),
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )

        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        mkdir_mock.assert_not_awaited()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_allows_folder_create_at_path_length_limit(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        absolute_dir = "/mnt/files/parent/documents"

        with (
            patch(
                "app.services.folder_create.FILES_MAX_PATH_LENGTH_BYTES",
                len(absolute_dir.encode("utf-8")),
            ),
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            folder = await create_folder(session, user, data)

        repository.insert.assert_awaited_once()
        self.assertEqual(parent.children_count, 1)
        repository.update.assert_awaited_once_with(parent)
        mkdir_mock.assert_awaited_once_with(absolute_dir)
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.FOLDER_CREATE_COMPLETED,
            session,
            folder,
        )

    async def test_raises_conflict_when_filesystem_directory_exists(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir_mock,
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )

        isdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        isfile_mock.assert_not_awaited()

        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        mkdir_mock.assert_not_awaited()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_filesystem_file_exists(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        parent = self._build_parent()

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain = AsyncMock(return_value=())

        lock_context = self._build_lock_context()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch(
                "app.services.folder_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.models.folder.get_config",
                return_value=config,
            ),
            patch(
                "app.services.folder_create.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_create.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir_mock,
            patch(
                "app.services.folder_create.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.folder_create.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.folder_create.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await create_folder(session, user, data)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(parent)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )

        isdir_mock.assert_awaited_once_with("/mnt/files/parent/documents")
        isfile_mock.assert_awaited_once_with("/mnt/files/parent/documents")

        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        mkdir_mock.assert_not_awaited()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
