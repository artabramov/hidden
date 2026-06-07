# tests/services/test_user_update.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.events import Events as E
from app.models.user import User
from app.services.user_update import update_user


class TestUpdateUser(unittest.IsolatedAsyncioTestCase):
    async def test_updates_display_name_only_when_summary_not_provided(self):
        session = AsyncMock()

        user = User()
        user.display_name = "Old Name"
        user.summary = "Old summary"

        data = MagicMock()
        data.display_name = "New Name"
        data.summary = "Ignored summary"
        data.model_fields_set = {"display_name"}

        repository = AsyncMock()

        with (
            patch(
                "app.services.user_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await update_user(session, user, data)

        self.assertEqual(user.display_name, "New Name")
        self.assertEqual(user.summary, "Old summary")

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_UPDATE_COMPLETED,
            session,
            user,
        )

    async def test_updates_display_name_summary_when_summary_provided(self):
        session = AsyncMock()

        user = User()
        user.display_name = "Old Name"
        user.summary = "Old summary"

        data = MagicMock()
        data.display_name = "New Name"
        data.summary = "New summary"
        data.model_fields_set = {"display_name", "summary"}

        repository = AsyncMock()

        with (
            patch(
                "app.services.user_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await update_user(session, user, data)

        self.assertEqual(user.display_name, "New Name")
        self.assertEqual(user.summary, "New summary")

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_UPDATE_COMPLETED,
            session,
            user,
        )
