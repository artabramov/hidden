import unittest
from unittest.mock import AsyncMock, patch
from app.routers.collection_delete_router import collection_delete
from app.hook import HOOK_AFTER_COLLECTION_DELETE
from app.error import E


class CollectionDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.collection_delete_router.Hook")
    @patch("app.routers.collection_delete_router.Repository")
    async def test_collection_delete_not_found(self, RepositoryMock, HookMock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await collection_delete(
                123, session=session_mock, cache=cache_mock,
                current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("collection_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.collection_delete_router.Hook")
    @patch("app.routers.collection_delete_router.Repository")
    async def test_collection_delete_success(self, RepositoryMock, HookMock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        collection_mock = AsyncMock(id=123)
        collection_mock.to_dict.return_value = {"id": 123}

        collection_repository_mock = AsyncMock()
        collection_repository_mock.select.return_value = collection_mock

        document_repository_mock = AsyncMock()

        RepositoryMock.side_effect = [
            collection_repository_mock, document_repository_mock]

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await collection_delete(
            123, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, {"collection_id": 123})
        collection_repository_mock.select.assert_called_with(id=123)
        document_repository_mock.delete_all_from_cache.assert_called_once()

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_COLLECTION_DELETE,
                                          collection_mock)


if __name__ == "__main__":
    unittest.main()
