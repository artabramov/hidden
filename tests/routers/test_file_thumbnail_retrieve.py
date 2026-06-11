# tests/routers/test_file_thumbnail_retrieve.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.user import User


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.file_thumbnail_retrieve import (  # noqa: E402
    file_thumbnail_retrieve_router,
)


class TestFileThumbnailRetrieveRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_response_with_thumbnail_bytes(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        response = MagicMock()

        with (
            patch(
                "app.routers.file_thumbnail_retrieve.retrieve_file_thumbnail",
                new_callable=AsyncMock,
                return_value=("image/png", b"thumbnail_bytes"),
            ) as mock_service,
            patch(
                "app.routers.file_thumbnail_retrieve.Response",
                return_value=response,
            ) as mock_response,
        ):
            out = await file_thumbnail_retrieve_router(
                file_id=42,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            file_id=42,
        )

        mock_response.assert_called_once_with(
            content=b"thumbnail_bytes",
            media_type="image/png",
        )

        self.assertIs(out, response)
