# tests/services/test_comment_create.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.locks import LockType
from app.models.file import File
from app.models.file_comment import FileComment
from app.models.file_revision import FileRevision  # noqa: F401
from app.models.file_tag import FileTag  # noqa: F401
from app.models.file_thumbnail import FileThumbnail  # noqa: F401
from app.models.folder import Folder  # noqa: F401
from app.models.user import User  # noqa: F401
from app.services.comment_create import create_comment


class TestCreateComment(unittest.IsolatedAsyncioTestCase):
    def _lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    async def test_creates_comment_writes_audit_commits_and_emits_hook(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.body = "Comment body."

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.id = 456
        file.file_folder = folder
        file.comments_count = 2
        file.get_absolute_path.return_value = "/vault/files/docs/note.txt"

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_create.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            comment = await create_comment(
                session=session,
                user=user,
                file_id=456,
                data=data,
            )

        file.get_absolute_path.assert_called_once_with(folder, parent_chain)
        lock_file_mock.assert_called_once_with(
            "/vault/files/docs/note.txt",
            LockType.WRITE,
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        repository.select.assert_awaited_once_with(File, obj_id=456)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.insert.assert_awaited_once()
        inserted_comment = repository.insert.await_args.args[0]

        self.assertIs(comment, inserted_comment)
        self.assertIsInstance(inserted_comment, FileComment)
        self.assertEqual(inserted_comment.file_id, 456)
        self.assertEqual(inserted_comment.created_by, 123)
        self.assertEqual(inserted_comment.body, "Comment body.")

        self.assertEqual(file.comments_count, 3)
        repository.update.assert_awaited_once_with(file)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.COMMENT_CREATE_COMPLETED,
            resource_type=FileComment.__tablename__,
            resource_id=inserted_comment.id,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.COMMENT_CREATE_COMPLETED,
            session,
            inserted_comment,
        )

    async def test_raises_not_found_when_file_missing(self):
        session = AsyncMock()

        user = MagicMock()
        data = MagicMock()
        data.body = "Comment body."

        repository = AsyncMock()
        repository.select.return_value = None

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_create.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await create_comment(
                    session=session,
                    user=user,
                    file_id=456,
                    data=data,
                )

        lock_file_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()

        repository.select.assert_awaited_once_with(File, obj_id=456)
        repository.select_parent_chain.assert_not_awaited()
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_protected(self):
        session = AsyncMock()

        user = MagicMock()
        data = MagicMock()
        data.body = "Comment body."

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = True

        file = MagicMock()
        file.id = 456
        file.file_folder = folder

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_create.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await create_comment(
                    session=session,
                    user=user,
                    file_id=456,
                    data=data,
                )

        lock_file_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()
        file.get_absolute_path.assert_not_called()

        repository.select.assert_awaited_once_with(File, obj_id=456)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_insert_failure_skips_update_audit_commit_emit_releases_lock(
        self,
    ):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.body = "Comment body."

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.id = 456
        file.file_folder = folder
        file.comments_count = 1
        file.get_absolute_path.return_value = "/vault/files/x.bin"

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain
        repository.insert.side_effect = RuntimeError("insert failed")

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_create.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            with self.assertRaises(RuntimeError):
                await create_comment(
                    session=session,
                    user=user,
                    file_id=456,
                    data=data,
                )

        lock_file_mock.assert_called_once_with(
            "/vault/files/x.bin", LockType.WRITE
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        self.assertEqual(file.comments_count, 1)
        repository.update.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_update_failure_after_insert_skip_audit_commit_releases_lock(
        self,
    ):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.body = "Comment body."

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.id = 456
        file.file_folder = folder
        file.comments_count = 0
        file.get_absolute_path.return_value = "/vault/files/y.dat"

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain
        repository.update.side_effect = RuntimeError("update failed")

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_create.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_create.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_create.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_create.locks.lock_file",
                return_value=lock_context,
            ),
        ):
            with self.assertRaises(RuntimeError):
                await create_comment(
                    session=session,
                    user=user,
                    file_id=456,
                    data=data,
                )

        repository.insert.assert_awaited_once()
        self.assertEqual(file.comments_count, 1)
        repository.update.assert_awaited_once_with(file)
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()
        lock_context.__aexit__.assert_awaited_once()
