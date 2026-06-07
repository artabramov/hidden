# tests/routers/test_file_rotate.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.routers.file_rotate import file_rotate_router
from app.schemas.file_rotate import FileRotateRequest


class TestFileRotateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_rotate_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        data = FileRotateRequest(angle=90)

        rotated_file = SimpleNamespace(id=10)

        with patch(
            "app.routers.file_rotate.rotate_file",
            new=AsyncMock(return_value=rotated_file),
        ) as rotate_file_mock:
            response = await file_rotate_router(
                file_id=10,
                data=data,
                session=session,
                current_user=current_user,
            )

        rotate_file_mock.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=10,
            data=data,
        )

        self.assertEqual(response.file_id, 10)
