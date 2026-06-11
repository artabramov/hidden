# tests/routers/test_file_upload.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import UploadFile

from app.models.user import User


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.file_upload import file_upload_router  # noqa: E402


class TestFileUploadRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_upload_response(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        uploaded_file = MagicMock(spec=UploadFile)

        uploaded = MagicMock()
        uploaded.id = 42

        with patch(
            "app.routers.file_upload.upload_file",
            new_callable=AsyncMock,
            return_value=uploaded,
        ) as mock_service:
            result = await file_upload_router(
                folder_id=7,
                file=uploaded_file,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            folder_id=7,
            uploaded_file=uploaded_file,
        )

        self.assertEqual(result.file_id, 42)
