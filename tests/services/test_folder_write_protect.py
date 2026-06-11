# tests/services/test_folder_write_protect.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.folder import Folder
from app.models.file import File  # noqa: F401
from app.models.file_comment import FileComment  # noqa: F401
from app.models.file_revision import FileRevision  # noqa: F401
from app.models.file_tag import FileTag  # noqa: F401
from app.models.file_thumbnail import FileThumbnail  # noqa: F401
from app.models.user import User
from app.services.folder_write_protect import change_folder_write_protect


class TestChangeFolderWriteProtected(unittest.IsolatedAsyncioTestCase):

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_data(self, value=True):
        data = MagicMock()
        data.is_write_protected = value
        return data

    def _build_folder(self, folder_id, is_write_protected=False):
        folder = Folder(
            parent_id=None,
            folder_parent=None,
            created_by=10,
            dirname="documents",
            summary=None,
            is_write_protected=is_write_protected,
        )
        folder.id = folder_id
        return folder

    async def test_raises_not_found_when_folder_missing(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(True)

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.folder_write_protect.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_write_protect.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_write_protect.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await change_folder_write_protect(
                    session=session,
                    user=user,
                    folder_id=42,
                    data=data,
                )

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.update.assert_not_awaited()
        session.commit.assert_not_awaited()

        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_sets_write_protected_true(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(True)
        folder = self._build_folder(42, is_write_protected=False)

        repository = AsyncMock()
        repository.select.return_value = folder

        with (
            patch(
                "app.services.folder_write_protect.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_write_protect.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_write_protect.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await change_folder_write_protect(
                session=session,
                user=user,
                folder_id=42,
                data=data,
            )

        self.assertIs(result, folder)
        self.assertIs(folder.is_write_protected, True)
        self.assertEqual(folder.updated_by, 10)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.update.assert_awaited_once_with(folder)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FOLDER_WRITE_PROTECT_COMPLETED,
            resource_type=Folder.__tablename__,
            resource_id=folder.id,
        )
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.FOLDER_WRITE_PROTECT_COMPLETED,
            session,
            folder,
        )

    async def test_sets_write_protected_false(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(False)
        folder = self._build_folder(42, is_write_protected=True)

        repository = AsyncMock()
        repository.select.return_value = folder

        with (
            patch(
                "app.services.folder_write_protect.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_write_protect.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_write_protect.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await change_folder_write_protect(
                session=session,
                user=user,
                folder_id=42,
                data=data,
            )

        self.assertIs(result, folder)
        self.assertIs(folder.is_write_protected, False)
        self.assertEqual(folder.updated_by, 10)

        repository.update.assert_awaited_once_with(folder)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once()

    async def test_does_not_check_recursive_write_protection(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(False)
        folder = self._build_folder(42, is_write_protected=True)
        folder.is_write_protected_recursive = MagicMock(
            side_effect=AssertionError(
                "recursive write protection must not be checked",
            ),
        )

        repository = AsyncMock()
        repository.select.return_value = folder

        with (
            patch(
                "app.services.folder_write_protect.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_write_protect.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_write_protect.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await change_folder_write_protect(
                session=session,
                user=user,
                folder_id=42,
                data=data,
            )

        folder.is_write_protected_recursive.assert_not_called()
