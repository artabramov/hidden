import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.collection_select import collection_select
from app.hook import HOOK_AFTER_COLLECTION_SELECT
from app.error import E
from app.config import get_config


class CollectionSelectRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.collection_select.Hook")
    @patch("app.routers.collection_select.Repository")
    async def test_collection_select_success(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        collection = AsyncMock(id=123)
        collection.to_dict = AsyncMock(
            return_value={"id": 123, "name": "dummy"})

        collection_repository = AsyncMock()
        collection_repository.select.return_value = collection
        RepositoryMock.return_value = collection_repository

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await collection_select(
            request, 123, session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, await collection.to_dict())
        collection_repository.select.assert_awaited_with(id=123)

        HookMock.assert_called_with(
            request, session, cache, current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_COLLECTION_SELECT, collection)

    @patch("app.routers.collection_select.Hook")
    @patch("app.routers.collection_select.Repository")
    async def test_collection_select_not_found(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        collection_repository = AsyncMock()
        collection_repository.select.return_value = None
        RepositoryMock.return_value = collection_repository

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await collection_select(
                request, 123, session=session, cache=cache,
                current_user=current_user)

        collection_repository.select.assert_awaited_with(id=123)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("collection_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
