# tests/services/test_user_select.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceForbiddenError, ResourceNotFoundError
from app.events import Events as E
from app.models.user import User
from app.services.user_select import select_user


class TestSelectUser(unittest.IsolatedAsyncioTestCase):
    async def test_returns_user_for_self_and_emits_hook(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 42
        current_user.can_admin = False

        selected_user = MagicMock(spec=User)
        selected_user.id = 42

        repository = AsyncMock()
        repository.select.return_value = selected_user

        with (
            patch(
                "app.services.user_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await select_user(session, current_user, 42)

        repository.select.assert_awaited_once_with(User, obj_id=42)
        emit_mock.assert_awaited_once_with(
            E.USER_SELECT_COMPLETED,
            session,
            selected_user,
        )
        self.assertIs(result, selected_user)

    async def test_returns_user_for_admin_and_emits_hook(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 1
        current_user.can_admin = True

        selected_user = MagicMock(spec=User)
        selected_user.id = 99

        repository = AsyncMock()
        repository.select.return_value = selected_user

        with (
            patch(
                "app.services.user_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await select_user(session, current_user, 99)

        repository.select.assert_awaited_once_with(User, obj_id=99)
        emit_mock.assert_awaited_once_with(
            E.USER_SELECT_COMPLETED,
            session,
            selected_user,
        )
        self.assertIs(result, selected_user)

    async def test_raises_not_found_when_user_does_not_exist(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 42
        current_user.can_admin = True

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.user_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await select_user(session, current_user, 99)

        repository.select.assert_awaited_once_with(User, obj_id=99)
        emit_mock.assert_not_awaited()

    async def test_raises_forbidden_when_non_admin_selects_other_user(self):
        session = AsyncMock()

        current_user = MagicMock(spec=User)
        current_user.id = 42
        current_user.can_admin = False

        selected_user = MagicMock(spec=User)
        selected_user.id = 99

        repository = AsyncMock()
        repository.select.return_value = selected_user

        with (
            patch(
                "app.services.user_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceForbiddenError):
                await select_user(session, current_user, 99)

        repository.select.assert_awaited_once_with(User, obj_id=99)
        emit_mock.assert_not_awaited()
