# tests/routers/test_file_tag_add.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.file_tag_add import file_tag_add_router  # noqa: E402
from app.schemas.file_tag_add import FileTagAddRequest  # noqa: E402


class TestFileTagAddRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        data = FileTagAddRequest(tag="Important123")

        with patch(
            "app.routers.file_tag_add.add_file_tag",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await file_tag_add_router(
                file_id=7,
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=7,
            data=data,
        )

        self.assertEqual(response.status_code, 204)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
