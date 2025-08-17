import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.routers.tag_list_router import tag_list
from app.hook import HOOK_AFTER_TAG_LIST


class TagListRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.tag_list_router.decrypt_str")
    @patch("app.routers.tag_list_router.Hook")
    @patch("app.routers.tag_list_router.EntityManager")
    async def test_tag_list(self, EntityManagerMock, HookMock,
                            decrypt_str_mock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()
        decrypt_str_mock.side_effect = ["one", "two"]

        entity_manager_mock = AsyncMock()
        data = [
            MagicMock(tag_value_encrypted="encrypted_one", documents_count=1),
            MagicMock(tag_value_encrypted="encrypted_two", documents_count=2),
        ]
        entity_manager_mock.select_rows.return_value = data
        EntityManagerMock.return_value = entity_manager_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await tag_list(
            request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, {"tags": [
            {"tag_value": "one", "documents_count": 1},
            {"tag_value": "two", "documents_count": 2}]})

        entity_manager_mock.select_rows.assert_called_once()
        decrypt_str_mock.assert_has_calls([
            call("encrypted_one"),
            call("encrypted_two")
        ])

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_TAG_LIST, [
            {"tag_value": "one", "documents_count": 1},
            {"tag_value": "two", "documents_count": 2}])


if __name__ == "__main__":
    unittest.main()
