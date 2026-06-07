# tests/routers/test_folder_write_protect.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from fastapi import status  # noqa: E402

from app.models.user import User  # noqa: E402
from app.routers.folder_write_protect import (  # noqa: E402
    folder_write_protect_router,
)
from app.schemas.folder_write_protect import (  # noqa: E402
    FolderWriteProtectRequest,
)


class TestFolderWriteProtectRouter(unittest.IsolatedAsyncioTestCase):

    async def test_write_protect_returns_204(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        data = FolderWriteProtectRequest(
            is_write_protected=True,
        )

        with patch(
            "app.routers.folder_write_protect.change_folder_write_protect",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await folder_write_protect_router(
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

    async def test_write_unprotect_returns_204(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        data = FolderWriteProtectRequest(
            is_write_protected=False,
        )

        with patch(
            "app.routers.folder_write_protect.change_folder_write_protect",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await folder_write_protect_router(
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
