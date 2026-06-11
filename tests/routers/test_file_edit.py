# tests/routers/test_file_edit.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.routers.file_edit import file_edit_router
from app.schemas.file_edit import FileEditRequest


class TestFileEditRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_edit_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        data = FileEditRequest(content="new text")

        edited_file = SimpleNamespace(id=10)

        with patch(
            "app.routers.file_edit.edit_file",
            new=AsyncMock(return_value=edited_file),
        ) as edit_file_mock:
            response = await file_edit_router(
                file_id=10,
                data=data,
                session=session,
                current_user=current_user,
            )

        edit_file_mock.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=10,
            data=data,
        )

        self.assertEqual(response.file_id, 10)
