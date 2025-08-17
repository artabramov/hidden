import unittest
from unittest.mock import AsyncMock, patch
from app.routers.document_list_router import document_list
from app.hook import HOOK_AFTER_DOCUMENT_LIST


class DocumentListRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.document_list_router.hash_str")
    @patch("app.routers.document_list_router.Hook")
    @patch("app.routers.document_list_router.Repository")
    async def test_document_list(self, RepositoryMock, HookMock, hash_str):
        schema_mock = AsyncMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        repository_mock = AsyncMock()
        documents = [AsyncMock(), AsyncMock()]
        repository_mock.select_all.return_value = documents
        repository_mock.count_all.return_value = 2
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await document_list(
            schema_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, {
            "documents": [await user.to_dict() for user in documents],
            "documents_count": 2,
        })

        repository_mock.select_all.assert_called_with(**schema_mock.__dict__)
        repository_mock.count_all.assert_called_with(**schema_mock.__dict__)

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_DOCUMENT_LIST,
                                          documents, 2)


if __name__ == "__main__":
    unittest.main()
