# tests/routers/test_file_tag_delete.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from fastapi import status  # noqa: E402
from app.models.user import User  # noqa: E402
from app.routers.file_tag_delete import file_tag_delete_router  # noqa: E402
from app.schemas.file_tag_path import FileTagPath  # noqa: E402


class TestFileTagDeleteRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        path = FileTagPath(file_id=7, tag="important")
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        with patch(
            "app.routers.file_tag_delete.delete_file_tag",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await file_tag_delete_router(
                path=path,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            path=path,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
