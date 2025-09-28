import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.document_select import document_select
from app.hook import HOOK_AFTER_DOCUMENT_SELECT
from app.error import E
from app.config import get_config


class DocumentSelectRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.document_select.Hook")
    @patch("app.routers.document_select.Repository")
    async def test_document_select_success(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        collection = AsyncMock(id=42)
        collection.to_dict = AsyncMock(
            return_value={"id": collection.id, "name": "col"})

        collection_repository = AsyncMock()
        collection_repository.select.return_value = collection

        document = AsyncMock(id=37, collection_id=collection.id)
        document.to_dict = AsyncMock(
            return_value={"id": document.id, "name": "doc"})

        document_repository = AsyncMock()
        document_repository.select.return_value = document

        RepositoryMock.side_effect = [
            collection_repository,
            document_repository
        ]

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await document_select(
            request, collection.id, document.id,
            session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, await document.to_dict())
        collection_repository.select.assert_awaited_with(id=collection.id)
        document_repository.select.assert_awaited_with(id=document.id)

        HookMock.assert_called_with(
            request, session, cache, current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_DOCUMENT_SELECT, document)

    @patch("app.routers.document_select.Hook")
    @patch("app.routers.document_select.Repository")
    async def test_document_select_collection_not_found(
            self, RepositoryMock, HookMock):

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
            await document_select(
                request, 42, 37,
                session=session, cache=cache,
                current_user=current_user
            )

        collection_repository.select.assert_awaited_with(id=42)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("collection_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()

    @patch("app.routers.document_select.Hook")
    @patch("app.routers.document_select.Repository")
    async def test_document_select_document_not_found(
            self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        collection = AsyncMock(id=42)
        collection.to_dict = AsyncMock(
            return_value={"id": collection.id, "name": "col"})

        collection_repository = AsyncMock()
        collection_repository.select.return_value = collection

        document_repository = AsyncMock()
        document_repository.select.return_value = None

        RepositoryMock.side_effect = [
            collection_repository,
            document_repository
        ]

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await document_select(
                request, collection.id, 37,
                session=session, cache=cache,
                current_user=current_user
            )

        collection_repository.select.assert_awaited_with(id=collection.id)
        document_repository.select.assert_awaited_with(id=37)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("document_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
