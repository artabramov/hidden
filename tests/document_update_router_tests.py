import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.routers.document_update_router import document_update
from app.hook import HOOK_AFTER_DOCUMENT_UPDATE
from app.config import get_config
from app.error import E

cfg = get_config()


class DocumentUpdateRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.document_update_router.Repository")
    @patch("app.routers.document_update_router.Hook")
    async def test_update_document_not_found(self, HookMock, RepositoryMock):
        schema_mock = AsyncMock(original_filename="original filename",
                                collection_id=123)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await document_update(
                234, schema=schema_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("document_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_update_router.Repository")
    @patch("app.routers.document_update_router.Hook")
    async def test_update_collection_not_found(self, HookMock, RepositoryMock):
        schema_mock = AsyncMock(original_filename="original filename",
                                collection_id=123)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        document_mock = MagicMock()

        repository_mock = AsyncMock()
        repository_mock.select.side_effect = [document_mock, None]
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await document_update(
                234, schema=schema_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("collection_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_update_router.CollectionLibrary")
    @patch("app.routers.document_update_router.Collection")
    @patch("app.routers.document_update_router.Document")
    @patch("app.routers.document_update_router.Repository")
    @patch("app.routers.document_update_router.Hook")
    async def test_update_success(self, HookMock, RepositoryMock, DocumentMock,
                                  CollectionMock, CollectionLibraryMock):
        schema_mock = AsyncMock(original_filename="original filename",
                                document_summary="document summary",
                                collection_id=123)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        document_mock = MagicMock()
        collection_mock = MagicMock()

        repository_mock = AsyncMock()
        repository_mock.select.side_effect = [document_mock, collection_mock]
        RepositoryMock.return_value = repository_mock

        collection_library_mock = AsyncMock()
        CollectionLibraryMock.return_value = collection_library_mock

        await document_update(
            234, schema=schema_mock, session=session_mock,
            cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(document_mock.original_filename, "original filename")
        self.assertEqual(document_mock.document_summary, "document summary")
        self.assertEqual(document_mock.collection_id, 123)

        self.assertListEqual(RepositoryMock.call_args_list, [
            call(session_mock, cache_mock, DocumentMock),
            call(session_mock, cache_mock, CollectionMock)])

        self.assertListEqual(repository_mock.select.call_args_list, [
            call(id=234), call(id=123)
        ])

        repository_mock.update.assert_called_with(document_mock)

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_DOCUMENT_UPDATE,
                                          document_mock)

        collection_library_mock.create_thumbnail.assert_called_with(
            collection_mock.id)


if __name__ == "__main__":
    unittest.main()
