# tests/services/test_comment_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import (
    ResourceForbiddenError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.locks import LockType
from app.models.file_comment import FileComment
from app.services.comment_delete import delete_comment


class TestDeleteComment(unittest.IsolatedAsyncioTestCase):
    def _lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    async def test_deletes_comment_writes_audit_commits_and_emits_hook(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.file_folder = folder
        file.comments_count = 3
        file.get_absolute_path.return_value = "/vault/files/docs/note.txt"

        comment = MagicMock(spec=FileComment)
        comment.id = 456
        comment.created_by = 123
        comment.comment_file = file

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = comment
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_delete.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            result = await delete_comment(
                session=session,
                user=user,
                comment_id=456,
            )

        file.get_absolute_path.assert_called_once_with(folder, parent_chain)
        lock_file_mock.assert_called_once_with(
            "/vault/files/docs/note.txt",
            LockType.WRITE,
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        self.assertIs(result, comment)

        repository.delete.assert_awaited_once_with(comment)
        self.assertEqual(file.comments_count, 2)
        repository.update.assert_awaited_once_with(file)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.COMMENT_DELETE_COMPLETED,
            resource_type=FileComment.__tablename__,
            resource_id=comment.id,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.COMMENT_DELETE_COMPLETED,
            session,
            comment,
        )

    async def test_raises_not_found_when_comment_missing(self):
        session = AsyncMock()

        user = MagicMock()

        repository = AsyncMock()
        repository.select.return_value = None

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_delete.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await delete_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                )

        lock_file_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_forbidden_user_is_not_owner(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        comment = MagicMock(spec=FileComment)
        comment.id = 456
        comment.created_by = 999

        repository = AsyncMock()
        repository.select.return_value = comment

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_delete.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            with self.assertRaises(ResourceForbiddenError):
                await delete_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                )

        lock_file_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_protected(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = True

        file = MagicMock()
        file.file_folder = folder

        comment = MagicMock(spec=FileComment)
        comment.id = 456
        comment.created_by = 123
        comment.comment_file = file

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = comment
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_delete.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await delete_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                )

        lock_file_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()
        file.get_absolute_path.assert_not_called()

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_delete_failure_skips_counter_update_commit_releases_lock(
        self,
    ):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.file_folder = folder
        file.comments_count = 5
        file.get_absolute_path.return_value = "/vault/files/x.bin"

        comment = MagicMock(spec=FileComment)
        comment.id = 456
        comment.created_by = 123
        comment.comment_file = file

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = comment
        repository.select_parent_chain.return_value = parent_chain
        repository.delete.side_effect = RuntimeError("delete failed")

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_delete.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
        ):
            with self.assertRaises(RuntimeError):
                await delete_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                )

        lock_file_mock.assert_called_once_with(
            "/vault/files/x.bin", LockType.WRITE
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        self.assertEqual(file.comments_count, 5)
        repository.update.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_update_failure_after_delete_skips_commit_releases_lock(
        self,
    ):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.file_folder = folder
        file.comments_count = 2
        file.get_absolute_path.return_value = "/vault/files/y.dat"

        comment = MagicMock(spec=FileComment)
        comment.id = 456
        comment.created_by = 123
        comment.comment_file = file

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = comment
        repository.select_parent_chain.return_value = parent_chain
        repository.update.side_effect = RuntimeError("update failed")

        lock_context = self._lock_context()

        with (
            patch(
                "app.services.comment_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.comment_delete.locks.lock_file",
                return_value=lock_context,
            ),
        ):
            with self.assertRaises(RuntimeError):
                await delete_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                )

        repository.delete.assert_awaited_once_with(comment)
        self.assertEqual(file.comments_count, 1)
        repository.update.assert_awaited_once_with(file)
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()
        lock_context.__aexit__.assert_awaited_once()
