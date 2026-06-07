# tests/services/test_file_tag_delete.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.models.file import File
from app.models.file_tag import FileTag
from app.schemas.file_tag_path import FileTagPath
from app.services.file_tag_delete import delete_file_tag


class TestDeleteFileTag(unittest.IsolatedAsyncioTestCase):

    async def test_deletes_file_tag_writes_audit_commits_and_emits_hook(self):
        session = AsyncMock()
        path = FileTagPath(file_id=456, tag="important")

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.id = 456
        file.file_folder = folder

        tag = MagicMock(spec=FileTag)
        tag.id = 789

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, tag]
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_tag_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            out = await delete_file_tag(
                session=session,
                path=path,
            )

        self.assertIsNone(out)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=456),
                call(FileTag, file_id=456, tag="important"),
            ],
        )
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.delete.assert_awaited_once_with(tag)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.TAG_DELETE_COMPLETED,
            resource_type=FileTag.__tablename__,
            resource_id=tag.id,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.TAG_DELETE_COMPLETED,
            session,
            tag,
        )

    async def test_raises_not_found_when_file_missing(self):
        session = AsyncMock()
        path = FileTagPath(file_id=456, tag="important")

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_tag_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await delete_file_tag(
                    session=session,
                    path=path,
                )

        repository.select.assert_awaited_once_with(File, obj_id=456)
        repository.select_parent_chain.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_protected(self):
        session = AsyncMock()
        path = FileTagPath(file_id=456, tag="important")

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

        with (
            patch(
                "app.services.file_tag_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await delete_file_tag(
                    session=session,
                    path=path,
                )

        repository.select.assert_awaited_once_with(File, obj_id=456)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.delete.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_returns_when_tag_missing(self):
        session = AsyncMock()
        path = FileTagPath(file_id=456, tag="important")

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.id = 456
        file.file_folder = folder

        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_tag_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            out = await delete_file_tag(
                session=session,
                path=path,
            )

        self.assertIsNone(out)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=456),
                call(FileTag, file_id=456, tag="important"),
            ],
        )
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.delete.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
