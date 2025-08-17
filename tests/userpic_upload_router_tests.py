import unittest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.userpic_upload_router import userpic_upload
from app.hook import HOOK_AFTER_USERPIC_UPLOAD
from app.error import E
from app.config import get_config

cfg = get_config()


class UserpicUploadRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.userpic_upload_router.Hook")
    async def test_userpic_upload_user_not_found(self, HookMock):
        request_mock = MagicMock()
        file_mock = AsyncMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await userpic_upload(
                234, request_mock, file=file_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("user_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.userpic_upload_router.Hook")
    async def test_userpic_upload_file_invalid(self, HookMock):
        request_mock = MagicMock()
        file_mock = AsyncMock(content_type="image/dummy")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await userpic_upload(
                123, request_mock, file=file_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "file_error")
        self.assertTrue("file" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.userpic_upload_router.encrypt_bytes")
    @patch("app.routers.userpic_upload_router.uuid")
    @patch("app.routers.userpic_upload_router.image_resize")
    @patch("app.routers.userpic_upload_router.Repository")
    @patch("app.routers.userpic_upload_router.FileManager",
           new_callable=AsyncMock)
    @patch("app.routers.userpic_upload_router.Hook")
    async def test_userpic_upload_success(self, HookMock, FileManagerMock,
                                          RepositoryMock, image_resize_mock,
                                          uuid_mock, encrypt_bytes_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filenam="dummy", content_type="image/jpeg")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123, has_userpic=True)
        uuid_mock.uuid4.return_value = "uuid"

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await userpic_upload(
            123, request_mock, file=file_mock, session=session_mock,
            cache=cache_mock, current_user=current_user_mock)

        self.assertDictEqual(result, {"user_id": 123})
        FileManagerMock.delete.assert_called_with(
            current_user_mock.userpic_path)
        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.USERPICS_PATH, "uuid"))
        FileManagerMock.read.assert_called_with(
            os.path.join(cfg.USERPICS_PATH, "uuid"))
        FileManagerMock.write.assert_called_with(
            os.path.join(cfg.USERPICS_PATH, "uuid"),
            encrypt_bytes_mock.return_value)

        encrypt_bytes_mock.assert_called_with(
            FileManagerMock.read.return_value)

        image_resize_mock.assert_called_with(
            os.path.join(cfg.USERPICS_PATH, "uuid"),
            cfg.USERPICS_WIDTH, cfg.USERPICS_HEIGHT, cfg.USERPICS_QUALITY)
        self.assertEqual(
            current_user_mock.userpic_filename, "uuid")
        repository_mock.update.assert_called_with(current_user_mock)

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(
            HOOK_AFTER_USERPIC_UPLOAD, current_user_mock)


if __name__ == "__main__":
    unittest.main()
