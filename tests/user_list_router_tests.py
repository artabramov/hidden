import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.config import get_config
from app.routers.user_list import user_list, User
from app.schemas.user_list import UserListRequest

cfg = get_config()


def _req():
    r = MagicMock()
    r.app = MagicMock()
    r.app.state = MagicMock()
    r.app.state.config = cfg
    r.state = MagicMock()
    r.state.log = MagicMock()
    return r


class UserListRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_list.Hook")
    @patch("app.routers.user_list.Repository")
    async def test_user_list_success(self, RepositoryMock, HookMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        schema = UserListRequest(
            offset=0,
            limit=10,
            order_by="id",
            order="asc",
            role__eq=None,
            username__ilike=" john ",
        )

        u1 = AsyncMock()
        u2 = AsyncMock()
        u1.to_dict.return_value = {"id": 1, "username": "john"}
        u2.to_dict.return_value = {"id": 2, "username": "jane"}

        repo = AsyncMock()
        repo.select_all.return_value = [u1, u2]
        repo.count_all.return_value = 2
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await user_list(
            request,
            schema=schema,
            session=session,
            cache=cache,
            current_user=current_user,
        )

        self.assertEqual(result["users_count"], 2)
        self.assertEqual(result["users"], [
            {"id": 1, "username": "john"},
            {"id": 2, "username": "jane"},
        ])

        expected_filters = schema.model_dump(exclude_none=True)
        RepositoryMock.assert_called_once_with(session, cache, User, cfg)
        repo.select_all.assert_awaited_with(**expected_filters)
        repo.count_all.assert_awaited_with(**expected_filters)

        HookMock.assert_called_with(request, session, cache,
                                    current_user=current_user)
        hook.call.assert_awaited()

    @patch("app.routers.user_list.Hook")
    @patch("app.routers.user_list.Repository")
    async def test_user_list_empty(self, RepositoryMock, HookMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        schema = UserListRequest(
            offset=0, limit=1, order_by="id", order="asc"
        )

        repo = AsyncMock()
        repo.select_all.return_value = []
        repo.count_all.return_value = 0
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await user_list(
            request,
            schema=schema,
            session=session,
            cache=cache,
            current_user=current_user,
        )

        self.assertEqual(result, {"users": [], "users_count": 0})
        hook.call.assert_awaited()
