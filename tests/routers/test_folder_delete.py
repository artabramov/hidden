# tests/routers/test_folder_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from fastapi import status  # noqa: E402

from app.models.user import User  # noqa: E402
from app.routers.folder_delete import folder_delete_router  # noqa: E402


class TestFolderDeleteRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        with patch(
            "app.routers.folder_delete.delete_folder",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await folder_delete_router(
                folder_id=42,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            folder_id=42,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
