import unittest
from unittest.mock import AsyncMock, patch
from app.routers.lock_retrieve_router import lock_retrieve
from app.hook import HOOK_AFTER_LOCK_RETRIEVE


class LockRetrieveRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.lock_retrieve_router.Hook")
    async def test_lock_retrieve(self, HookMock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await lock_retrieve(
            session=session_mock, cache=cache_mock)

        self.assertDictEqual(result, {"lock_exists": False})

        HookMock.assert_called_with(session_mock, cache_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_LOCK_RETRIEVE, False)


if __name__ == "__main__":
    unittest.main()
