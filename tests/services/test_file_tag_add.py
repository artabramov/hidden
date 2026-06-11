# tests/services/test_file_tag_add.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from sqlalchemy.exc import IntegrityError

from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.models.file import File
from app.models.file_tag import FileTag
from app.services.file_tag_add import add_file_tag


class TestCreateFileTag(unittest.IsolatedAsyncioTestCase):
    async def test_creates_file_tag_writes_audit_commits_and_emits_hook(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.tag = "important"

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
                "app.services.file_tag_add.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_add.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_add.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await add_file_tag(
                session=session,
                user=user,
                file_id=456,
                data=data,
            )

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

        repository.insert.assert_awaited_once()
        inserted_tag = repository.insert.await_args.args[0]

        self.assertIsInstance(inserted_tag, FileTag)
        self.assertEqual(inserted_tag.file_id, 456)
        self.assertEqual(inserted_tag.created_by, 123)
        self.assertEqual(inserted_tag.tag, "important")

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.TAG_ADD_COMPLETED,
            resource_type=FileTag.__tablename__,
            resource_id=inserted_tag.id,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.TAG_ADD_COMPLETED,
            session,
            inserted_tag,
        )

    async def test_raises_not_found_when_file_missing(self):
        session = AsyncMock()

        user = MagicMock()
        data = MagicMock()
        data.tag = "important"

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_tag_add.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_add.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_add.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await add_file_tag(
                    session=session,
                    user=user,
                    file_id=456,
                    data=data,
                )

        repository.select.assert_awaited_once_with(File, obj_id=456)
        repository.select_parent_chain.assert_not_awaited()
        repository.insert.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_protected(self):
        session = AsyncMock()

        user = MagicMock()
        data = MagicMock()
        data.tag = "important"

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
                "app.services.file_tag_add.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_add.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_add.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await add_file_tag(
                    session=session,
                    user=user,
                    file_id=456,
                    data=data,
                )

        repository.select.assert_awaited_once_with(File, obj_id=456)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )
        repository.insert.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_returns_when_tag_already_exists(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.tag = "important"

        folder = MagicMock()
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False

        file = MagicMock()
        file.id = 456
        file.file_folder = folder

        existing_tag = MagicMock(spec=FileTag)
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, existing_tag]
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_tag_add.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_add.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_add.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await add_file_tag(
                session=session,
                user=user,
                file_id=456,
                data=data,
            )

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

        repository.insert.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_on_insert_integrity_error(
        self,
    ):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.tag = "important"

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
        repository.insert.side_effect = IntegrityError(None, None, None)

        with (
            patch(
                "app.services.file_tag_add.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_tag_add.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_tag_add.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await add_file_tag(
                session=session,
                user=user,
                file_id=456,
                data=data,
            )

        repository.insert.assert_awaited_once()
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
