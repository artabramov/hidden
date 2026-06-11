# tests/routers/test_file_move.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.routers.file_move import file_move_router
from app.schemas.file_move import FileMoveRequest


class TestFileMoveRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_move_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        data = FileMoveRequest(folder_id=2)

        moved_file = SimpleNamespace(
            id=10,
            folder_id=2,
        )

        with patch(
            "app.routers.file_move.move_file",
            new=AsyncMock(return_value=moved_file),
        ) as move_file_mock:
            response = await file_move_router(
                file_id=10,
                data=data,
                session=session,
                current_user=current_user,
            )

        move_file_mock.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=10,
            data=data,
        )

        self.assertEqual(response.file_id, 10)
        self.assertEqual(response.folder_id, 2)
