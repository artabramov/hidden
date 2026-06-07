# tests/routers/test_folder_update.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from fastapi import status  # noqa: E402

from app.models.user import User  # noqa: E402
from app.routers.folder_update import folder_update_router  # noqa: E402
from app.schemas.folder_update import FolderUpdateRequest  # noqa: E402


class TestFolderUpdateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_update_returns_204(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        data = FolderUpdateRequest(
            dirname="documents",
            summary="Folder summary.",
        )

        with patch(
            "app.routers.folder_update.update_folder",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await folder_update_router(
                folder_id=42,
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            folder_id=42,
            data=data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    async def test_update_passes_none_summary(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        data = FolderUpdateRequest(
            dirname="documents",
            summary=None,
        )

        with patch(
            "app.routers.folder_update.update_folder",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await folder_update_router(
                folder_id=42,
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            folder_id=42,
            data=data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
