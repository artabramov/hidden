# tests/routers/test_file_update.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.routers.file_update import file_update_router
from app.schemas.file_update import FileUpdateRequest


class TestFileUpdateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_update_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        data = FileUpdateRequest(
            filename="new-document.txt",
            summary="New summary",
        )

        updated_file = SimpleNamespace(id=10)

        with patch(
            "app.routers.file_update.update_file",
            new=AsyncMock(return_value=updated_file),
        ) as update_file_mock:
            response = await file_update_router(
                file_id=10,
                data=data,
                session=session,
                current_user=current_user,
            )

        update_file_mock.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=10,
            data=data,
        )

        self.assertEqual(response.file_id, 10)
