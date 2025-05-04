import unittest
from unittest.mock import AsyncMock, patch
from app.routers.collection_list_router import collection_list
from app.hook import HOOK_AFTER_COLLECTION_LIST


class CollectionListRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.collection_list_router.Hook")
    @patch("app.routers.collection_list_router.Repository")
    async def test_collection_list(self, RepositoryMock, HookMock):
        schema_mock = AsyncMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        repository_mock = AsyncMock()
        collections = [AsyncMock(), AsyncMock()]
        repository_mock.select_all.return_value = collections
        repository_mock.count_all.return_value = 2
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await collection_list(
            schema_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, {
            "collections": [await user.to_dict() for user in collections],
            "collections_count": 2,
        })

        repository_mock.select_all.assert_called_with(**schema_mock.__dict__)
        repository_mock.count_all.assert_called_with(**schema_mock.__dict__)

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_COLLECTION_LIST,
                                          collections, 2)


if __name__ == "__main__":
    unittest.main()
