import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.collection_update_router import collection_update
from app.hook import HOOK_AFTER_COLLECTION_UPDATE
from app.config import get_config
from app.error import E

cfg = get_config()


class CollectionUpdateRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.collection_update_router.Repository")
    @patch("app.routers.collection_update_router.Hook")
    async def test_collection_update_not_found(
            self, HookMock, RepositoryMock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(collection_name="collection name",
                                collection_summary="lorem ipsum")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await collection_update(
                234, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("collection_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.collection_update_router.hash_str")
    @patch("app.routers.collection_update_router.Repository")
    @patch("app.routers.collection_update_router.Hook")
    async def test_collection_update_name_exists(
            self, HookMock, RepositoryMock, hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(collection_name="collection name",
                                collection_summary="lorem ipsum")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.select.return_value = AsyncMock()
        repository_mock.exists.return_value = True
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await collection_update(
                234, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_exists")
        self.assertTrue("collection_name" in context.exception.detail[0]["loc"])  # noqa E501

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.collection_update_router.hash_str")
    @patch("app.routers.collection_update_router.Repository")
    @patch("app.routers.collection_update_router.Hook")
    async def test_collection_update_success(self, HookMock, RepositoryMock,
                                             hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(collection_name="collection name",
                                collection_summary="lorem ipsum")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        collection_mock = AsyncMock(id=234)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.select.return_value = collection_mock
        repository_mock.exists.return_value = False
        RepositoryMock.return_value = repository_mock

        result = await collection_update(
                234, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertDictEqual(result, {
            "collection_id": collection_mock.id,
        })

        self.assertEqual(collection_mock.collection_name, "collection name")
        self.assertEqual(collection_mock.collection_summary, "lorem ipsum")
        hash_str_mock.assert_called_with("collection name")
        repository_mock.select.assert_called_with(id=234)
        repository_mock.exists.assert_called_with(
            collection_name_hash__eq=hash_str_mock.return_value,
            id__ne=collection_mock.id)

        HookMock.assert_called_with(request_mock.app, session_mock, cache_mock,
                                    current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_COLLECTION_UPDATE,
                                          collection_mock)


if __name__ == "__main__":
    unittest.main()
