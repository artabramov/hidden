# tests/services/test_user_role_change.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceForbiddenError, ResourceNotFoundError
from app.events import Events as E
from app.models.user import User
from app.services.user_role_change import change_user_role


class TestChangeUserRole(unittest.IsolatedAsyncioTestCase):
    async def test_raises_forbidden_when_user_updates_self(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 42

        data = MagicMock()
        data.role.value = "admin"
        data.is_active = True

        with (
            patch("app.services.user_role_change.ORMRepository") as repo_cls,
            patch(
                "app.services.user_role_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceForbiddenError):
                await change_user_role(
                    session=session,
                    current_user=current_user,
                    user_id=42,
                    data=data,
                )

        repo_cls.assert_not_called()
        emit_mock.assert_not_awaited()

    async def test_raises_not_found_when_target_user_does_not_exist(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 1

        data = MagicMock()
        data.role.value = "editor"
        data.is_active = True

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.user_role_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_role_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await change_user_role(
                    session=session,
                    current_user=current_user,
                    user_id=99,
                    data=data,
                )

        repository.select.assert_awaited_once_with(User, obj_id=99)
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_updates_role_and_active_flag_and_emits_hook(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 1

        target_user = MagicMock(spec=User)
        target_user.role = "reader"
        target_user.is_active = False

        data = MagicMock()
        data.role.value = "admin"
        data.is_active = True

        repository = AsyncMock()
        repository.select.return_value = target_user

        with (
            patch(
                "app.services.user_role_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_role_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_role_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await change_user_role(
                session=session,
                current_user=current_user,
                user_id=99,
                data=data,
            )

        repository.select.assert_awaited_once_with(User, obj_id=99)
        self.assertEqual(target_user.role, "admin")
        self.assertIs(target_user.is_active, True)
        repository.update.assert_awaited_once_with(target_user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_ROLE_CHANGE_COMPLETED,
            session,
            target_user,
        )

    async def test_allows_admin_role_revocation_from_other_user(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 1

        target_user = MagicMock(spec=User)
        target_user.role = "admin"
        target_user.is_active = True

        data = MagicMock()
        data.role.value = "reader"
        data.is_active = True

        repository = AsyncMock()
        repository.select.return_value = target_user

        with (
            patch(
                "app.services.user_role_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_role_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_role_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await change_user_role(
                session=session,
                current_user=current_user,
                user_id=2,
                data=data,
            )

        self.assertEqual(target_user.role, "reader")
        self.assertIs(target_user.is_active, True)
        repository.update.assert_awaited_once_with(target_user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_ROLE_CHANGE_COMPLETED,
            session,
            target_user,
        )

    async def test_allows_deactivation_of_other_user(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 1

        target_user = MagicMock(spec=User)
        target_user.role = "editor"
        target_user.is_active = True

        data = MagicMock()
        data.role.value = "editor"
        data.is_active = False

        repository = AsyncMock()
        repository.select.return_value = target_user

        with (
            patch(
                "app.services.user_role_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_role_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_role_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await change_user_role(
                session=session,
                current_user=current_user,
                user_id=77,
                data=data,
            )

        self.assertEqual(target_user.role, "editor")
        self.assertIs(target_user.is_active, False)
        repository.update.assert_awaited_once_with(target_user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_ROLE_CHANGE_COMPLETED,
            session,
            target_user,
        )
