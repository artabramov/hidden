import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import os
from app.hook import HOOK_AFTER_USERPIC_DELETE
from app.routers.userpic_delete import userpic_delete


class UserpicDeleteRouterTests(unittest.IsolatedAsyncioTestCase):
    def _mk_request(self, thumbs_dir="/tmp/thumbs", lru=None, fm=None,
                    log=None):
        config = SimpleNamespace(THUMBNAILS_DIR=thumbs_dir)
        state = SimpleNamespace(
            config=config,
            lru=lru or MagicMock(),
            file_manager=fm or AsyncMock(),
            log=log or MagicMock(),
        )
        # на всякий случай, чтобы debug() точно существовал
        state.log.debug = getattr(state.log, "debug", MagicMock())
        app = SimpleNamespace(state=state)
        return SimpleNamespace(app=app, state=state)

    async def test_422_when_user_id_mismatch(self):
        request = self._mk_request()
        session = MagicMock()
        cache = MagicMock()
        # has_thumbnail=True, но user_id отличается — должно дать 422
        current_user = SimpleNamespace(
            id=1,
            has_thumbnail=True,
            user_thumbnail=SimpleNamespace(path=MagicMock()),
        )

        with self.assertRaises(Exception) as ctx:
            await userpic_delete(
                request=request, user_id=2, session=session, cache=cache,
                current_user=current_user
            )
        self.assertEqual(getattr(ctx.exception, "status_code", None), 422)

        request.app.state.lru.delete.assert_not_called()
        request.app.state.file_manager.delete.assert_not_awaited()

    @patch("app.routers.userpic_delete.Hook")
    @patch("app.routers.userpic_delete.Repository")
    async def test_success_deletes_from_lru_disk_updates_user_and_calls_hook(
        self, RepoMock, HookMock
    ):
        repo_inst = AsyncMock()
        RepoMock.return_value = repo_inst

        hook_inst = AsyncMock()
        HookMock.return_value = hook_inst

        thumbs_dir = "/var/app/thumbs"
        request = self._mk_request(thumbs_dir=thumbs_dir)
        session = MagicMock()
        cache = MagicMock()

        # user_thumbnail.path(config) должен вернуть полный путь
        expected_path = os.path.join(thumbs_dir, "pic.jpg")
        user_thumbnail = SimpleNamespace(
            path=MagicMock(return_value=expected_path)
        )
        current_user = SimpleNamespace(
            id=42,
            has_thumbnail=True,
            user_thumbnail=user_thumbnail,
        )

        result = await userpic_delete(
            request=request, user_id=42, session=session, cache=cache,
            current_user=current_user
        )

        request.app.state.lru.delete.assert_called_once_with(expected_path)
        request.app.state.file_manager.delete.assert_awaited_once_with(
            expected_path)

        RepoMock.assert_called_once()               # репозиторий создан
        repo_inst.update.assert_awaited_once()      # пользователь обновлён

        HookMock.assert_called_once_with(
            request, session, cache, current_user=current_user
        )
        hook_inst.call.assert_awaited_once_with(HOOK_AFTER_USERPIC_DELETE)

        request.state.log.debug.assert_called()
        self.assertIsNone(current_user.user_thumbnail)
        self.assertEqual(result, {"user_id": 42})
