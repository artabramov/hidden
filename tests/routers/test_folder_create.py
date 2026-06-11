# tests/routers/test_folder_create.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.folder_create import folder_create_router  # noqa: E402
from app.schemas.folder_create import FolderCreateRequest  # noqa: E402


class TestFolderCreateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_folder_create_response(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        data = FolderCreateRequest(
            parent_id=None,
            dirname="docs",
            summary="",
        )

        folder = MagicMock()
        folder.id = 42

        with patch(
            "app.routers.folder_create.create_folder",
            new_callable=AsyncMock,
            return_value=folder,
        ) as mock_service:
            result = await folder_create_router(
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            data=data,
        )

        self.assertEqual(result.folder_id, 42)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
