# tests/services/test_file_starred_change.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.file import File
from app.models.user import User
from app.services.file_starred_change import change_file_starred


class TestChangeFileStarred(unittest.IsolatedAsyncioTestCase):

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_data(self, value=True):
        data = MagicMock()
        data.is_starred = value
        return data

    def _build_file(self, file_id, is_starred=False):
        file = MagicMock(spec=File)
        file.id = file_id
        file.is_starred = is_starred
        file.updated_by = None
        return file

    async def test_raises_not_found_when_file_missing(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(True)

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_starred_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_starred_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_starred_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await change_file_starred(
                    session=session,
                    user=user,
                    file_id=42,
                    data=data,
                )

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()

        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_sets_starred_true(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(True)
        file = self._build_file(42, is_starred=False)

        repository = AsyncMock()
        repository.select.return_value = file

        with (
            patch(
                "app.services.file_starred_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_starred_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_starred_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await change_file_starred(
                session=session,
                user=user,
                file_id=42,
                data=data,
            )

        self.assertIs(result, file)
        self.assertIs(file.is_starred, True)
        self.assertEqual(file.updated_by, 10)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.update.assert_awaited_once_with(file)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_STARRED_CHANGE_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=file.id,
        )
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.FILE_STARRED_CHANGE_COMPLETED,
            session,
            file,
        )

    async def test_sets_starred_false(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(False)
        file = self._build_file(42, is_starred=True)

        repository = AsyncMock()
        repository.select.return_value = file

        with (
            patch(
                "app.services.file_starred_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_starred_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_starred_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await change_file_starred(
                session=session,
                user=user,
                file_id=42,
                data=data,
            )

        self.assertIs(result, file)
        self.assertIs(file.is_starred, False)
        self.assertEqual(file.updated_by, 10)

        repository.update.assert_awaited_once_with(file)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once()

    async def test_does_not_check_recursive_write_protection(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(True)
        file = self._build_file(42, is_starred=False)
        file.file_folder = MagicMock()
        file.file_folder.is_write_protected_recursive = MagicMock(
            side_effect=AssertionError(
                "recursive write protection must not be checked",
            ),
        )

        repository = AsyncMock()
        repository.select.return_value = file

        with (
            patch(
                "app.services.file_starred_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_starred_change.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_starred_change.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await change_file_starred(
                session=session,
                user=user,
                file_id=42,
                data=data,
            )

        repository.select_parent_chain.assert_not_awaited()
        file.file_folder.is_write_protected_recursive.assert_not_called()
