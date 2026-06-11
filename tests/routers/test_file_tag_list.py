# tests/routers/test_file_tag_list.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.user import User
from app.schemas.file_tag_list import TagListRequest

from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.file_tag_list import tag_list_router  # noqa: E402


class TestTagListRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_tag_list(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        params = TagListRequest(limit=3)

        service_tags = [("python", 10), ("fastapi", 7), ("docs", 3)]

        with patch(
            "app.routers.file_tag_list.list_tags",
            new_callable=AsyncMock,
            return_value=service_tags,
        ) as mock_service:
            out = await tag_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            params=params,
        )

        self.assertEqual(len(out), 3)
        self.assertEqual(out[0].tag, "python")
        self.assertEqual(out[0].usage_count, 10)
        self.assertEqual(out[1].tag, "fastapi")
        self.assertEqual(out[1].usage_count, 7)
        self.assertEqual(out[2].tag, "docs")
        self.assertEqual(out[2].usage_count, 3)

    async def test_returns_empty_list(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        params = TagListRequest()

        with patch(
            "app.routers.file_tag_list.list_tags",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_service:
            out = await tag_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            params=params,
        )

        self.assertEqual(out, [])

    async def test_passes_custom_limit_to_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        params = TagListRequest(limit=100)

        with patch(
            "app.routers.file_tag_list.list_tags",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_service:
            await tag_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            params=params,
        )
        self.assertEqual(mock_service.call_args.kwargs["params"].limit, 100)
