import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.document_delete_router import document_delete
from app.hook import HOOK_AFTER_DOCUMENT_DELETE
from app.config import get_config
from app.error import E

cfg = get_config()


class DocumentDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.document_delete_router.Repository")
    @patch("app.routers.document_delete_router.Hook")
    async def test_document_delete_error(self, HookMock, RepositoryMock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await document_delete(
                123, session=session_mock, cache=cache_mock,
                current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("document_id" in context.exception.detail[0]["loc"])

        repository_mock.select.assert_called_with(id=123)
        repository_mock.delete.assert_not_called()

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_delete_router.Repository")
    @patch("app.routers.document_delete_router.Hook")
    @patch("app.routers.document_delete_router.CollectionLibrary")
    async def test_document_delete_success(self, CollectionLibraryMock,
                                           HookMock, RepositoryMock):
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        document_mock = MagicMock(id=123)
        document_mock.document_collection = MagicMock(id=1)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = document_mock
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        collection_library_mock = AsyncMock()
        CollectionLibraryMock.return_value = collection_library_mock

        result = await document_delete(
            123, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertDictEqual(result, {"document_id": document_mock.id})

        repository_mock.select.assert_called_with(id=123)
        repository_mock.delete.assert_called_with(document_mock)

        HookMock.assert_called_with(
            session_mock, cache_mock, current_user=current_user_mock)
        hook_mock.call.assert_called_with(
            HOOK_AFTER_DOCUMENT_DELETE, document_mock)

        CollectionLibraryMock.assert_called_with(session_mock, cache_mock)
        collection_library_mock.create_thumbnail.assert_called_with(
            document_mock.document_collection.id)


if __name__ == "__main__":
    unittest.main()
