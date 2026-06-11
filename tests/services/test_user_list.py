# tests/services/test_user_list.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.events import Events as E
from app.models.user import User
from app.services.user_list import list_users


class TestListUsers(unittest.IsolatedAsyncioTestCase):
    def _build_params(self, **kwargs):
        params = MagicMock()
        params.model_dump.return_value = kwargs
        return params

    async def test_lists_users_without_filters(self):
        session = AsyncMock()

        params = self._build_params()

        users = [MagicMock(spec=User), MagicMock(spec=User)]
        repository = AsyncMock()
        repository.count_all.return_value = 2
        repository.select_all.return_value = users

        with (
            patch(
                "app.services.user_list.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_list.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            result_users, result_count = await list_users(session, params)

        repository.count_all.assert_awaited_once_with(User)
        repository.select_all.assert_awaited_once_with(User)

        emit_mock.assert_awaited_once_with(
            E.USER_LIST_COMPLETED,
            session,
            users,
        )

        self.assertEqual(result_users, users)
        self.assertEqual(result_count, 2)

    async def test_applies_username_ilike_filter(self):
        session = AsyncMock()

        params = self._build_params(username__ilike="alice")

        repository = AsyncMock()
        repository.count_all.return_value = 1
        repository.select_all.return_value = ["user"]

        with (
            patch(
                "app.services.user_list.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_list.hooks.emit",
                new=AsyncMock()
            ),
        ):
            await list_users(session, params)

        repository.count_all.assert_awaited_once_with(
            User,
            username__ilike="%alice%",
        )
        repository.select_all.assert_awaited_once_with(
            User,
            username__ilike="%alice%",
        )

    async def test_applies_display_name_ilike_filter(self):
        session = AsyncMock()

        params = self._build_params(display_name__ilike="john")

        repository = AsyncMock()
        repository.count_all.return_value = 1
        repository.select_all.return_value = ["user"]

        with (
            patch(
                "app.services.user_list.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_list.hooks.emit",
                new=AsyncMock()
            ),
        ):
            await list_users(session, params)

        repository.count_all.assert_awaited_once_with(
            User,
            display_name__ilike="%john%",
        )
        repository.select_all.assert_awaited_once_with(
            User,
            display_name__ilike="%john%",
        )

    async def test_applies_both_ilike_filters(self):
        session = AsyncMock()

        params = self._build_params(
            username__ilike="alice",
            display_name__ilike="john",
        )

        repository = AsyncMock()
        repository.count_all.return_value = 0
        repository.select_all.return_value = []

        with (
            patch(
                "app.services.user_list.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_list.hooks.emit",
                new=AsyncMock()
            ),
        ):
            await list_users(session, params)

        repository.count_all.assert_awaited_once_with(
            User,
            username__ilike="%alice%",
            display_name__ilike="%john%",
        )
        repository.select_all.assert_awaited_once_with(
            User,
            username__ilike="%alice%",
            display_name__ilike="%john%",
        )

    async def test_passes_through_other_filters(self):
        session = AsyncMock()

        params = self._build_params(
            role="admin",
            is_active=True,
        )

        repository = AsyncMock()
        repository.count_all.return_value = 0
        repository.select_all.return_value = []

        with (
            patch(
                "app.services.user_list.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_list.hooks.emit",
                new=AsyncMock()
            ),
        ):
            await list_users(session, params)

        repository.count_all.assert_awaited_once_with(
            User,
            role="admin",
            is_active=True,
        )
        repository.select_all.assert_awaited_once_with(
            User,
            role="admin",
            is_active=True,
        )

    async def test_excludes_none_filters_from_model_dump(self):
        session = AsyncMock()

        params = MagicMock()
        params.model_dump.return_value = {}

        repository = AsyncMock()
        repository.count_all.return_value = 0
        repository.select_all.return_value = []

        with (
            patch(
                "app.services.user_list.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_list.hooks.emit",
                new=AsyncMock()
            ),
        ):
            await list_users(session, params)

        params.model_dump.assert_called_once_with(exclude_none=True)
        repository.count_all.assert_awaited_once_with(User)
        repository.select_all.assert_awaited_once_with(User)
