# tests/routers/test_file_download.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.user import User


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.file_download import file_download_router  # noqa: E402


class TestFileDownloadRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_response(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        file = SimpleNamespace(
            filename="document.txt",
            mimetype="text/plain",
        )
        file_path = "/storage/docs/document.txt"
        response = MagicMock()

        with (
            patch(
                "app.routers.file_download.download_file",
                new_callable=AsyncMock,
                return_value=(file, file_path),
            ) as mock_service,
            patch(
                "app.routers.file_download.FileResponse",
                return_value=response,
            ) as mock_response,
        ):
            out = await file_download_router(
                file_id=42,
                revision_number=0,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            file_id=42,
            revision_number=0,
        )

        mock_response.assert_called_once_with(
            path="/storage/docs/document.txt",
            media_type="text/plain",
            filename="document.txt",
        )

        self.assertIs(out, response)
