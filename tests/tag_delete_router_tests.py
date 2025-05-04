import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.tag_delete_router import tag_delete
from app.hook import HOOK_AFTER_TAG_DELETE
from app.config import get_config
from app.error import E

cfg = get_config()


class TagDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.tag_delete_router.Repository")
    @patch("app.routers.tag_delete_router.Hook")
    async def test_tag_delete_document_not_found(
            self, HookMock, RepositoryMock):
        schema_mock = AsyncMock(tag_value="tag")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.select.return_value = False
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await tag_delete(123, schema=schema_mock,
                             session=session_mock, cache=cache_mock)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("document_id" in context.exception.detail[0]["loc"])

        repository_mock.select.assert_called_with(id=123)
        repository_mock.delete_from_cache.assert_not_called()

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.tag_delete_router.hash_str")
    @patch("app.routers.tag_delete_router.Repository")
    @patch("app.routers.tag_delete_router.Hook")
    async def test_tag_not_found(self, HookMock, RepositoryMock,
                                 hash_str_mock):
        schema_mock = AsyncMock(tag_value="tag")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        document_mock = MagicMock(id=234)
        document_repository_mock = AsyncMock()
        document_repository_mock.select.return_value = document_mock

        tag_repository_mock = AsyncMock()
        tag_repository_mock.select.return_value = None

        RepositoryMock.side_effect = [
            document_repository_mock, tag_repository_mock]

        with self.assertRaises(E) as context:
            await tag_delete(123, schema=schema_mock,
                             session=session_mock, cache=cache_mock)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("tag_value" in context.exception.detail[0]["loc"])

        document_repository_mock.select.assert_called_with(id=123)
        tag_repository_mock.select.assert_called_with(
            document_id__eq=document_mock.id,
            tag_value_hash__eq=hash_str_mock.return_value)

        tag_repository_mock.delete.assert_not_called()
        document_repository_mock.delete_from_cache.assert_not_called()

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.tag_delete_router.hash_str")
    @patch("app.routers.tag_delete_router.Repository")
    @patch("app.routers.tag_delete_router.Hook")
    async def test_tag_delete(self, HookMock, RepositoryMock, hash_str_mock):
        schema_mock = AsyncMock(tag_value="tag")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = MagicMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        document_mock = MagicMock(id=234)
        document_repository_mock = AsyncMock()
        document_repository_mock.select.return_value = document_mock

        tag_mock = MagicMock(id=123)
        tag_repository_mock = AsyncMock()
        tag_repository_mock.select.return_value = tag_mock

        RepositoryMock.side_effect = [
            document_repository_mock, tag_repository_mock]

        result = await tag_delete(
            123, schema=schema_mock, session=session_mock,
            cache=cache_mock, current_user=current_user_mock)
        self.assertDictEqual(result, {"tag_id": tag_mock.id})

        document_repository_mock.select.assert_called_with(id=123)
        tag_repository_mock.select.assert_called_with(
            document_id__eq=document_mock.id,
            tag_value_hash__eq=hash_str_mock.return_value)

        tag_repository_mock.delete.assert_called_with(tag_mock)
        document_repository_mock.delete_from_cache.assert_called_with(
            document_mock)

        HookMock.assert_called_with(
            session_mock, cache_mock, current_user=current_user_mock)
        hook_mock.call.assert_called_with(
            HOOK_AFTER_TAG_DELETE, document_mock, tag_mock)


if __name__ == "__main__":
    unittest.main()
