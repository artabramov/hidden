# tests/services/test_comment_update.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import (
    ResourceForbiddenError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.models.file_comment import FileComment
from app.services.comment_update import update_comment


class TestUpdateComment(unittest.IsolatedAsyncioTestCase):

    async def test_updates_comment_writes_audit_commits_and_emits_hook(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.body = "Updated body."

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

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

        with (
            patch(
                "app.services.comment_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await update_comment(
                session=session,
                user=user,
                comment_id=456,
                data=data,
            )

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        self.assertIs(result, comment)
        self.assertEqual(comment.body, "Updated body.")

        repository.update.assert_awaited_once_with(comment)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.COMMENT_UPDATE_COMPLETED,
            resource_type=FileComment.__tablename__,
            resource_id=comment.id,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.COMMENT_UPDATE_COMPLETED,
            session,
            comment,
        )

    async def test_raises_not_found_when_comment_missing(self):
        session = AsyncMock()

        user = MagicMock()
        data = MagicMock()
        data.body = "Updated body."

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.comment_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await update_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                    data=data,
                )

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_forbidden_user_is_not_owner(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.body = "Updated body."

        comment = MagicMock(spec=FileComment)
        comment.id = 456
        comment.created_by = 999

        repository = AsyncMock()
        repository.select.return_value = comment

        with (
            patch(
                "app.services.comment_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceForbiddenError):
                await update_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                    data=data,
                )

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_protected(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.body = "Updated body."

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

        with (
            patch(
                "app.services.comment_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.comment_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.comment_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await update_comment(
                    session=session,
                    user=user,
                    comment_id=456,
                    data=data,
                )

        repository.select.assert_awaited_once_with(
            FileComment,
            obj_id=456,
        )
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
