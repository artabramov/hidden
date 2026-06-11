# tests/routers/test_file_starred_change.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.routers.file_starred_change import file_starred_change_router
from app.schemas.file_starred_change import FileStarredChangeRequest


class TestFileStarredChangeRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_starred_change_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        data = FileStarredChangeRequest(is_starred=True)

        changed_file = SimpleNamespace(id=10)

        with patch(
            "app.routers.file_starred_change.change_file_starred",
            new=AsyncMock(return_value=changed_file),
        ) as change_file_starred_mock:
            response = await file_starred_change_router(
                file_id=10,
                data=data,
                session=session,
                current_user=current_user,
            )

        change_file_starred_mock.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=10,
            data=data,
        )

        self.assertEqual(response.file_id, 10)
