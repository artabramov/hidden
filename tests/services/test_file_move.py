# tests/services/test_file_move.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from sqlalchemy.exc import IntegrityError

from app.constants import FILES_MAX_PATH_LENGTH_BYTES
from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.locks import LockType
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.schemas.file_move import FileMoveRequest
from app.services.file_move import move_file


class TestMoveFile(unittest.IsolatedAsyncioTestCase):

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_folder(self, folder_id, files_count=0):
        folder = MagicMock(spec=Folder)
        folder.id = folder_id
        folder.files_count = files_count
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False
        return folder

    def _build_file(self, source_folder):
        file = MagicMock(spec=File)
        file.id = 42
        file.folder_id = source_folder.id
        file.filename = "document.txt"
        file.updated_by = None
        file.file_folder = source_folder
        file.get_absolute_path.side_effect = [
            "/mnt/files/source/document.txt",
            "/mnt/files/destination/document.txt",
        ]
        return file

    async def test_moves_file_writes_audit_commits_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        source_parent_chain = (MagicMock(),)
        destination_parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [
            source_parent_chain,
            destination_parent_chain,
        ]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir_mock,
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await move_file(
                session=session,
                user=user,
                file_id=42,
                data=data,
            )

        self.assertIs(result, file)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=42),
                call(Folder, obj_id=2),
                call(
                    File,
                    filename="document.txt",
                    folder_id=2,
                ),
            ],
        )
        self.assertEqual(
            repository.select_parent_chain.await_args_list,
            [
                call(source_folder),
                call(destination_folder),
            ],
        )

        source_folder.is_write_protected_recursive.assert_called_once_with(
            source_parent_chain,
        )
        destination_folder.is_write_protected_recursive.assert_called_once_with(  # noqa: E501
            destination_parent_chain,
        )

        self.assertEqual(
            file.get_absolute_path.call_args_list,
            [
                call(source_folder, source_parent_chain),
                call(destination_folder, destination_parent_chain),
            ],
        )

        lock_directory_mock.assert_called_once_with(
            "/mnt/files",
            LockType.WRITE,
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        isdir_mock.assert_awaited_once_with(
            "/mnt/files/destination/document.txt",
        )
        isfile_mock.assert_awaited_once_with(
            "/mnt/files/destination/document.txt",
        )
        rename_mock.assert_awaited_once_with(
            "/mnt/files/source/document.txt",
            "/mnt/files/destination/document.txt",
        )

        self.assertEqual(file.folder_id, 2)
        self.assertEqual(file.updated_by, 10)
        self.assertEqual(source_folder.files_count, 2)
        self.assertEqual(destination_folder.files_count, 6)

        self.assertEqual(
            repository.update.await_args_list,
            [
                call(file),
                call(source_folder),
                call(destination_folder),
            ],
        )

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_MOVE_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=42,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.FILE_MOVE_COMPLETED,
            session,
            file,
        )

    async def test_raises_not_found_file_missing(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        repository = AsyncMock()
        repository.select.return_value = None

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_source_protected(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        source_folder.is_write_protected_recursive.return_value = True
        file = self._build_file(source_folder)
        source_parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = source_parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(
            source_folder,
        )
        source_folder.is_write_protected_recursive.assert_called_once_with(
            source_parent_chain,
        )

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_not_found_destination_missing(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        file = self._build_file(source_folder)
        source_parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = source_parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=42),
                call(Folder, obj_id=2),
            ],
        )
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_returns_file_when_destination_same(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=1)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = source_folder
        file = self._build_file(source_folder)
        source_parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder]
        repository.select_parent_chain.return_value = source_parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await move_file(
                session=session,
                user=user,
                file_id=42,
                data=data,
            )

        self.assertIs(result, file)
        self.assertEqual(source_folder.files_count, 3)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=42),
                call(Folder, obj_id=1),
            ],
        )
        repository.select_parent_chain.assert_awaited_once_with(
            source_folder,
        )
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_destination_protected(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        destination_folder.is_write_protected_recursive.return_value = True
        file = self._build_file(source_folder)

        source_parent_chain = (MagicMock(),)
        destination_parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder]
        repository.select_parent_chain.side_effect = [
            source_parent_chain,
            destination_parent_chain,
        ]

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        destination_folder.is_write_protected_recursive.assert_called_once_with(  # noqa: E501
            destination_parent_chain,
        )

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_path_too_long(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)
        file.get_absolute_path.side_effect = [
            "/mnt/files/source/document.txt",
            "/mnt/files/" + ("a" * FILES_MAX_PATH_LENGTH_BYTES),
        ]

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder]
        repository.select_parent_chain.side_effect = [(), ()]

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_db_file_exists(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)
        existing_file = MagicMock(spec=File)

        repository = AsyncMock()
        repository.select.side_effect = [
            file,
            destination_folder,
            existing_file,
        ]
        repository.select_parent_chain.side_effect = [(), ()]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        rename_mock.assert_not_awaited()
        isdir_mock.assert_not_awaited()
        isfile_mock.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_destination_is_dir(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir_mock,
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        isdir_mock.assert_awaited_once_with(
            "/mnt/files/destination/document.txt",
        )
        isfile_mock.assert_not_awaited()
        rename_mock.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_destination_is_file(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        isfile_mock.assert_awaited_once_with(
            "/mnt/files/destination/document.txt",
        )
        rename_mock.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rollback_restores_file_raises_integrity_error(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]
        repository.update.side_effect = IntegrityError(None, None, None)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call(
                    "/mnt/files/source/document.txt",
                    "/mnt/files/destination/document.txt",
                ),
                call(
                    "/mnt/files/destination/document.txt",
                    "/mnt/files/source/document.txt",
                ),
            ],
        )

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_integrity_error_restore_rename_fails_still_raises_conflict(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]
        repository.update.side_effect = IntegrityError(None, None, None)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        rename_mock = AsyncMock(
            side_effect=[
                None,
                OSError("restore rename failed"),
            ],
        )

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.rename",
                new=rename_mock,
            ),
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertLogs(
                "app.services.file_move", level="WARNING"
            ) as log_cap:
                with self.assertRaises(ResourceConflictError):
                    await move_file(
                        session=session,
                        user=user,
                        file_id=42,
                        data=data,
                    )

        messages = " ".join(r.getMessage() for r in log_cap.records)
        self.assertIn(E.FILE_MOVE_RESTORE_FAILED, messages)
        self.assertIn(E.FILE_MOVE_FILENAME_CONFLICT, messages)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call(
                    "/mnt/files/source/document.txt",
                    "/mnt/files/destination/document.txt",
                ),
                call(
                    "/mnt/files/destination/document.txt",
                    "/mnt/files/source/document.txt",
                ),
            ],
        )

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_restores_file_and_reraises_generic_error(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        error = RuntimeError("audit failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(side_effect=error),
            ),
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        self.assertIs(cm.exception, error)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call(
                    "/mnt/files/source/document.txt",
                    "/mnt/files/destination/document.txt",
                ),
                call(
                    "/mnt/files/destination/document.txt",
                    "/mnt/files/source/document.txt",
                ),
            ],
        )

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_preserves_original_error_when_restore_fails(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        original_error = RuntimeError("audit failed")
        restore_error = RuntimeError("restore failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        rename_mock = AsyncMock(side_effect=[None, restore_error])

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.rename",
                new=rename_mock,
            ),
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(side_effect=original_error),
            ),
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertLogs(
                "app.services.file_move", level="WARNING"
            ) as log_cap:
                with self.assertRaises(RuntimeError) as cm:
                    await move_file(
                        session=session,
                        user=user,
                        file_id=42,
                        data=data,
                    )

        self.assertIs(cm.exception, original_error)

        messages = " ".join(r.getMessage() for r in log_cap.records)
        self.assertIn(E.FILE_MOVE_RESTORE_FAILED, messages)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call(
                    "/mnt/files/source/document.txt",
                    "/mnt/files/destination/document.txt",
                ),
                call(
                    "/mnt/files/destination/document.txt",
                    "/mnt/files/source/document.txt",
                ),
            ],
        )

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_integrity_error_on_rename_skips_fs_restore_branch(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(
                    side_effect=IntegrityError(None, None, None),
                ),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        rename_mock.assert_awaited_once_with(
            "/mnt/files/source/document.txt",
            "/mnt/files/destination/document.txt",
        )
        repository.rollback.assert_awaited_once()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_generic_exception_on_rename_skips_fs_restore_branch(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileMoveRequest(folder_id=2)

        source_folder = self._build_folder(1, files_count=3)
        destination_folder = self._build_folder(2, files_count=5)
        file = self._build_file(source_folder)

        boom = RuntimeError("rename failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, destination_folder, None]
        repository.select_parent_chain.side_effect = [(), ()]

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_move.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_move.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_move.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_move.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_move.rename",
                new=AsyncMock(side_effect=boom),
            ) as rename_mock,
            patch(
                "app.services.file_move.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_move.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await move_file(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        self.assertIs(cm.exception, boom)
        rename_mock.assert_awaited_once_with(
            "/mnt/files/source/document.txt",
            "/mnt/files/destination/document.txt",
        )
        repository.rollback.assert_awaited_once()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
