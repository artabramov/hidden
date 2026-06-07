# tests/routers/test_file_flip.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.routers.file_flip import file_flip_router
from app.schemas.file_flip import FileFlipRequest


class TestFileFlipRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_flip_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        data = FileFlipRequest(axis="horizontal")

        flipped_file = SimpleNamespace(id=10)

        with patch(
            "app.routers.file_flip.flip_file",
            new=AsyncMock(return_value=flipped_file),
        ) as flip_file_mock:
            response = await file_flip_router(
                file_id=10,
                data=data,
                session=session,
                current_user=current_user,
            )

        flip_file_mock.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=10,
            data=data,
        )

        self.assertEqual(response.file_id, 10)
