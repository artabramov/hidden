import unittest
from unittest.mock import AsyncMock, patch
from app.routers.collection_insert_router import collection_insert
from app.hook import HOOK_AFTER_COLLECTION_INSERT
from app.config import get_config
from app.error import E

cfg = get_config()


class CollectionInsertRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.collection_insert_router.hash_str")
    @patch("app.routers.collection_insert_router.Repository")
    @patch("app.routers.collection_insert_router.Hook")
    async def test_collection_insert_collection_exists(
            self, HookMock, RepositoryMock, hash_str_mock):
        schema_mock = AsyncMock(collection_name="collection name",
                                collection_summary="lorem ipsum")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = True
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await collection_insert(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_exists")
        self.assertTrue("collection_name" in context.exception.detail[0]["loc"])  # noqa E501

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.collection_insert_router.hash_str")
    @patch("app.routers.collection_insert_router.Collection")
    @patch("app.routers.collection_insert_router.Repository")
    @patch("app.routers.collection_insert_router.Hook")
    async def test_collection_insert_success(self, HookMock, RepositoryMock,
                                             CollectionMock, hash_str_mock):
        schema_mock = AsyncMock(collection_name="collection name",
                                collection_summary="lorem ipsum")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = False
        RepositoryMock.return_value = repository_mock

        result = await collection_insert(
                schema=schema_mock, session=session_mock, cache=cache_mock,
                current_user=current_user_mock)

        self.assertDictEqual(result, {
            "collection_id": CollectionMock.return_value.id,
        })

        CollectionMock.assert_called_with(
            123, schema_mock.collection_name,
            collection_summary=schema_mock.collection_summary)

        repository_mock.insert.assert_called_with(CollectionMock.return_value)

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_COLLECTION_INSERT,
                                          CollectionMock.return_value)


if __name__ == "__main__":
    unittest.main()
