import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.error import E
from app.hook import HOOK_AFTER_COLLECTION_INSERT
from app.routers.collection_insert import collection_insert
from app.schemas.collection_insert import CollectionInsertRequest


class CollectionInsertRouterTest(unittest.IsolatedAsyncioTestCase):
    def _make_request(self, *, documents_dir="/collections", fm=None):
        cfg = MagicMock()
        cfg.DOCUMENTS_DIR = documents_dir

        request = MagicMock()
        request.app = MagicMock()
        request.app.state.config = cfg
        request.app.state.file_manager = fm if fm is not None else MagicMock()
        request.state.log = MagicMock()
        request.state.log.debug = MagicMock()
        return request, cfg, request.app.state.file_manager

    async def test_collection_insert_success(self):
        request, cfg, fm = self._make_request()
        fm.mkdir = AsyncMock()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = MagicMock()
        current_user.id = 42

        repo = AsyncMock()
        repo.exists = AsyncMock(return_value=False)

        async def _insert_side_effect(entity):
            entity.id = 777

        repo.insert = AsyncMock(side_effect=_insert_side_effect)

        hook_instance = MagicMock()
        hook_instance.call = AsyncMock()

        with patch("app.routers.collection_insert.Repository", return_value=repo) as RepositoryMock, \
             patch("app.routers.collection_insert.Hook", return_value=hook_instance) as HookMock:

            schema = CollectionInsertRequest(readonly=False, name="Inbox", summary=None)
            result = await collection_insert(
                request=request,
                schema=schema,
                session=session,
                cache=cache,
                current_user=current_user,
            )

        self.assertEqual(result, {"collection_id": 777})

        RepositoryMock.assert_called_once()

        repo.exists.assert_awaited_once_with(name__eq="Inbox")

        expected_dir = os.path.join(cfg.DOCUMENTS_DIR, "Inbox")
        fm.mkdir.assert_awaited_once_with(expected_dir)

        repo.insert.assert_awaited_once()
        inserted_entity = repo.insert.call_args.args[0]
        self.assertEqual(inserted_entity.name, "Inbox")
        self.assertFalse(inserted_entity.readonly)
        self.assertIsNone(inserted_entity.summary)
        self.assertEqual(inserted_entity.id, 777)

        HookMock.assert_called_once()
        hook_instance.call.assert_awaited_once()
        args, _ = hook_instance.call.call_args
        self.assertEqual(args[0], HOOK_AFTER_COLLECTION_INSERT)
        self.assertIs(args[1], inserted_entity)

        request.state.log.debug.assert_called()

    async def test_collection_insert_conflict(self):
        request, cfg, fm = self._make_request()
        fm.mkdir = AsyncMock()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = MagicMock()

        repo = AsyncMock()
        repo.exists = AsyncMock(return_value=True)
        repo.insert = AsyncMock()

        hook_instance = MagicMock()
        hook_instance.call = AsyncMock()

        with patch("app.routers.collection_insert.Repository", return_value=repo), \
             patch("app.routers.collection_insert.Hook", return_value=hook_instance):

            schema = CollectionInsertRequest(readonly=True, name="Projects", summary="x")
            with self.assertRaises(E) as ctx:
                await collection_insert(
                    request=request,
                    schema=schema,
                    session=session,
                    cache=cache,
                    current_user=current_user,
                )

        self.assertEqual(ctx.exception.status_code, 422)
        fm.mkdir.assert_not_called()
        repo.insert.assert_not_called()
        hook_instance.call.assert_not_called()

    async def test_collection_insert_mkdir_failure(self):
        request, cfg, fm = self._make_request()
        fm.mkdir = AsyncMock(side_effect=OSError("mkdir failed"))

        session = AsyncMock()
        cache = AsyncMock()
        current_user = MagicMock()

        repo = AsyncMock()
        repo.exists = AsyncMock(return_value=False)
        repo.insert = AsyncMock()

        hook_instance = MagicMock()
        hook_instance.call = AsyncMock()

        with patch("app.routers.collection_insert.Repository", return_value=repo), \
             patch("app.routers.collection_insert.Hook", return_value=hook_instance):

            schema = CollectionInsertRequest(readonly=False, name="Broken", summary=None)
            with self.assertRaises(OSError):
                await collection_insert(
                    request=request,
                    schema=schema,
                    session=session,
                    cache=cache,
                    current_user=current_user,
                )

        repo.insert.assert_not_called()
        hook_instance.call.assert_not_called()
