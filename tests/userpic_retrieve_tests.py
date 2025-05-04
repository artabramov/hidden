import os
import unittest
from unittest.mock import AsyncMock, patch
from starlette.responses import Response
from app.routers.userpic_retrieve_router import userpic_retrieve
from app.error import E
from app.config import get_config

cfg = get_config()


class UserpicDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.userpic_retrieve_router.lru", new_callable=AsyncMock)
    async def test_userpic_not_found(self, lru_mock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        lru_mock.load.return_value = None
        userpic_filename = "filename"

        with self.assertRaises(E) as context:
            await userpic_retrieve(
                userpic_filename, session=session_mock, cache=cache_mock,
                current_user=current_user_mock)

        lru_mock.load.assert_called_with(
            os.path.join(cfg.USERPICS_PATH, "filename"))

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "file_not_found")
        self.assertTrue("userpic_filename" in context.exception.detail[0]["loc"])  # noqa E501

    @patch("app.routers.userpic_retrieve_router.lru", new_callable=AsyncMock)
    async def test_userpic_retrieved(self, lru_mock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        lru_mock.load.return_value = b"userpic"
        userpic_filename = "filename"

        result = await userpic_retrieve(
                userpic_filename, session=session_mock, cache=cache_mock,
                current_user=current_user_mock)

        lru_mock.load.assert_called_with(
            os.path.join(cfg.USERPICS_PATH, "filename"))

        self.assertTrue(isinstance(result, Response))
        result.body = lru_mock.load.return_value
        result.media_type = "image/jpeg"
        result.charset = "utf-8"
        result.userpic_filename = "filename"


if __name__ == "__main__":
    unittest.main()
