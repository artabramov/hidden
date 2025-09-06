import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import os
from app.routers.userpic_delete import userpic_delete


class UserpicDeleteRouterTests(unittest.IsolatedAsyncioTestCase):
    def _mk_request(self, thumbs_dir="/tmp/thumbs", lru=None, fm=None, log=None):
        config = SimpleNamespace(THUMBNAILS_DIR=thumbs_dir)
        state = SimpleNamespace(config=config, lru=lru or MagicMock(), file_manager=fm or AsyncMock())
        if log is None:
            log = MagicMock()
        state.log = log
        app = SimpleNamespace(state=state)
        return SimpleNamespace(app=app, state=state)

    async def test_422_when_user_id_mismatch(self):
        request = self._mk_request()
        session = MagicMock()
        cache = MagicMock()
        current_user = SimpleNamespace(id=1, has_thumbnail=True,
                                       user_thumbnail=SimpleNamespace(filename="a.jpg"))

        with self.assertRaises(Exception) as ctx:
            await userpic_delete(
                user_id=2, request=request, session=session, cache=cache, current_user=current_user
            )
        self.assertEqual(getattr(ctx.exception, "status_code", None), 422)

        request.app.state.lru.delete.assert_not_called()
        request.app.state.file_manager.delete.assert_not_awaited()

    async def test_404_when_no_thumbnail(self):
        request = self._mk_request()
        session = MagicMock()
        cache = MagicMock()
        current_user = SimpleNamespace(id=7, has_thumbnail=False, user_thumbnail=None)

        with self.assertRaises(Exception) as ctx:
            await userpic_delete(
                user_id=7, request=request, session=session, cache=cache, current_user=current_user
            )
        self.assertEqual(getattr(ctx.exception, "status_code", None), 404)

        request.app.state.lru.delete.assert_not_called()
        request.app.state.file_manager.delete.assert_not_awaited()

    @patch("app.routers.userpic_delete.Hook")
    @patch("app.routers.userpic_delete.Repository")
    async def test_success_deletes_from_lru_disk_updates_user_and_calls_hook(self, RepoMock, HookMock):
        repo_inst = AsyncMock()
        RepoMock.return_value = repo_inst

        hook_inst = AsyncMock()
        HookMock.return_value = hook_inst

        thumbs_dir = "/var/app/thumbs"
        request = self._mk_request(thumbs_dir=thumbs_dir)
        session = MagicMock()
        cache = MagicMock()
        current_user = SimpleNamespace(
            id=42,
            has_thumbnail=True,
            user_thumbnail=SimpleNamespace(filename="pic.jpg"),
        )

        result = await userpic_delete(
            user_id=42, request=request, session=session, cache=cache, current_user=current_user
        )

        expected_path = os.path.join(thumbs_dir, "pic.jpg")

        request.app.state.lru.delete.assert_called_once_with(expected_path)
        request.app.state.file_manager.delete.assert_awaited_once_with(expected_path)
        repo_inst.update.assert_awaited_once()
        HookMock.assert_called_once()
        hook_inst.call.assert_awaited_once()

        self.assertIsNone(current_user.user_thumbnail)
        self.assertEqual(result, {"user_id": 42})
