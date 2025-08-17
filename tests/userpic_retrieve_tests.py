import os
import unittest
from unittest.mock import AsyncMock, patch
from starlette.responses import Response
from app.routers.userpic_retrieve_router import userpic_retrieve
from app.config import get_config

cfg = get_config()


class UserpicDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.userpic_retrieve_router.decrypt_bytes")
    @patch("app.routers.userpic_retrieve_router.FileManager", new_callable=AsyncMock)  # noqa E501
    @patch("app.routers.userpic_retrieve_router.lru", new_callable=AsyncMock)
    async def test_userpic_not_found_in_lru(self, lru_mock, FileManagerMock,
                                            decrypt_bytes_mock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        lru_mock.load.return_value = None
        userpic_filename = "filename"

        result = await userpic_retrieve(
            userpic_filename, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)
        self.assertTrue(isinstance(result, Response))

        FileManagerMock.read.assert_called_with(
            os.path.join(cfg.USERPICS_PATH, userpic_filename)
        )
        decrypt_bytes_mock.assert_called_with(
            FileManagerMock.read.return_value
        )
        lru_mock.save.assert_called_with(
            userpic_filename, decrypt_bytes_mock.return_value
        )

    @patch("app.routers.userpic_retrieve_router.lru", new_callable=AsyncMock)
    async def test_userpic_found_in_lru(self, lru_mock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        lru_mock.load.return_value = b"userpic"
        userpic_filename = "filename"

        result = await userpic_retrieve(
            userpic_filename, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)
        self.assertTrue(isinstance(result, Response))

        lru_mock.load.assert_called_with(userpic_filename)
        lru_mock.save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
