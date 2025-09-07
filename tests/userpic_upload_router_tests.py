import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.error import E
from app.hook import HOOK_AFTER_USERPIC_UPLOAD
from app.routers.userpic_upload import userpic_upload


class UserpicUploadRouterTest(unittest.IsolatedAsyncioTestCase):
    def _make_request(self, *, dir_="/thumbs", w=128, h=128, q=85, fm=None):
        cfg = MagicMock()
        cfg.THUMBNAILS_DIR = dir_
        cfg.THUMBNAILS_WIDTH = w
        cfg.THUMBNAILS_HEIGHT = h
        cfg.THUMBNAILS_QUALITY = q

        request = MagicMock()
        request.app = MagicMock()
        request.app.state.config = cfg
        request.app.state.file_manager = fm if fm is not None else MagicMock()
        request.state.log = MagicMock()
        request.state.log.debug = MagicMock()
        return request, cfg, request.app.state.file_manager

    def _make_file(self, *, filename="in.png", content_type="image/png"):
        f = MagicMock()
        f.filename = filename
        f.content_type = content_type
        return f

    @patch("app.routers.userpic_upload.IMAGE_EXTENSION", ".jpeg")
    @patch("app.routers.userpic_upload.CONST_IMAGE_MIMETYPES", {"image/png"})
    @patch("app.routers.userpic_upload.uuid.uuid4")
    @patch("app.routers.userpic_upload.image_resize", new_callable=AsyncMock)
    @patch("app.routers.userpic_upload.UserThumbnail")
    @patch("app.routers.userpic_upload.Repository")
    @patch("app.routers.userpic_upload.Hook")
    async def test_userpic_upload_success_no_existing(
        self,
        HookMock,
        RepositoryMock,
        UserThumbnailMock,
        image_resize_mock,
        uuid4_mock,
    ):
        uuid4_mock.return_value = "11111111-1111-1111-1111-111111111111"

        hook_instance = MagicMock()
        hook_instance.call = AsyncMock()
        HookMock.return_value = hook_instance

        fm = MagicMock()
        fm.upload = AsyncMock()
        fm.filesize = AsyncMock(return_value=12345)
        fm.mimetype = AsyncMock(return_value="image/jpeg")
        fm.checksum = AsyncMock(return_value="deadbeef" * 8)
        fm.delete = AsyncMock()

        request, cfg, file_manager = self._make_request(fm=fm)
        session = AsyncMock()
        cache = AsyncMock()

        current_user = MagicMock()
        current_user.id = 42
        current_user.has_thumbnail = False

        repo = AsyncMock()
        RepositoryMock.return_value = repo

        file = self._make_file(filename="input.png", content_type="image/png")

        result = await userpic_upload(
            42, request, file=file, session=session, cache=cache, current_user=current_user
        )

        self.assertEqual(result, {"user_id": 42})

        expected_name = "11111111-1111-1111-1111-111111111111.jpeg"
        expected_path = os.path.join(cfg.THUMBNAILS_DIR, expected_name)

        file_manager.upload.assert_awaited_once_with(file, expected_path)
        image_resize_mock.assert_awaited_once_with(
            expected_path, cfg.THUMBNAILS_WIDTH, cfg.THUMBNAILS_HEIGHT, cfg.THUMBNAILS_QUALITY
        )
        file_manager.filesize.assert_awaited_once_with(expected_path)
        file_manager.mimetype.assert_called_once_with(expected_path)
        file_manager.checksum.assert_awaited_once_with(expected_path)

        UserThumbnailMock.assert_called_once()
        args, kwargs = UserThumbnailMock.call_args
        self.assertEqual(args[0], 42)
        self.assertEqual(args[1], expected_name)
        self.assertEqual(args[2], cfg.THUMBNAILS_WIDTH)
        self.assertEqual(args[3], cfg.THUMBNAILS_HEIGHT)
        self.assertEqual(args[4], "deadbeef" * 8)
        self.assertEqual(args[5], 12345)
        self.assertEqual(args[6], "image/jpeg")

        self.assertIs(current_user.user_thumbnail, UserThumbnailMock.return_value)
        repo.update.assert_awaited_once_with(current_user)

        HookMock.assert_called_once()
        hook_instance.call.assert_awaited_once_with(HOOK_AFTER_USERPIC_UPLOAD)
        request.state.log.debug.assert_called()

    @patch("app.routers.userpic_upload.IMAGE_EXTENSION", ".jpeg")
    @patch("app.routers.userpic_upload.CONST_IMAGE_MIMETYPES", {"image/png"})
    @patch("app.routers.userpic_upload.uuid.uuid4")
    @patch("app.routers.userpic_upload.image_resize", new_callable=AsyncMock)
    @patch("app.routers.userpic_upload.UserThumbnail")
    @patch("app.routers.userpic_upload.Repository")
    @patch("app.routers.userpic_upload.Hook")
    async def test_userpic_upload_success_with_existing(
        self,
        HookMock,
        RepositoryMock,
        UserThumbnailMock,
        image_resize_mock,
        uuid4_mock,
    ):
        uuid4_mock.return_value = "22222222-2222-2222-2222-222222222222"

        hook_instance = MagicMock()
        hook_instance.call = AsyncMock()
        HookMock.return_value = hook_instance

        fm = MagicMock()
        fm.upload = AsyncMock()
        fm.filesize = AsyncMock(return_value=999)
        fm.mimetype = AsyncMock(return_value="image/jpeg")
        fm.checksum = AsyncMock(return_value="aa" * 32)
        fm.delete = AsyncMock()

        request, cfg, file_manager = self._make_request(fm=fm)
        session = AsyncMock()
        cache = AsyncMock()

        old_thumb = MagicMock()
        old_thumb.filename = "old.jpeg"

        current_user = MagicMock()
        current_user.id = 7
        current_user.user_thumbnail = old_thumb

        repo = AsyncMock()
        RepositoryMock.return_value = repo

        file = self._make_file(filename="pic.png", content_type="image/png")

        result = await userpic_upload(
            7, request, file=file, session=session, cache=cache, current_user=current_user
        )
        self.assertEqual(result, {"user_id": 7})

        file_manager.delete.assert_awaited_once_with(os.path.join(cfg.THUMBNAILS_DIR, "old.jpeg"))
        self.assertGreaterEqual(repo.update.await_count, 2)

        expected_name = "22222222-2222-2222-2222-222222222222.jpeg"
        expected_path = os.path.join(cfg.THUMBNAILS_DIR, expected_name)

        file_manager.upload.assert_awaited_once_with(file, expected_path)
        image_resize_mock.assert_awaited_once()
        file_manager.filesize.assert_awaited_once_with(expected_path)
        file_manager.mimetype.assert_called_once_with(expected_path)
        file_manager.checksum.assert_awaited_once_with(expected_path)

        UserThumbnailMock.assert_called_once()
        HookMock.assert_called_once()
        hook_instance.call.assert_awaited_once_with(HOOK_AFTER_USERPIC_UPLOAD)
        request.state.log.debug.assert_called()

    @patch("app.routers.userpic_upload.CONST_IMAGE_MIMETYPES", {"image/png"})
    async def test_userpic_upload_invalid_mime(self):
        request, _, _ = self._make_request()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = MagicMock()
        current_user.id = 1

        file = self._make_file(filename="doc.pdf", content_type="application/pdf")

        with self.assertRaises(E) as ctx:
            await userpic_upload(
                1, request, file=file, session=session, cache=cache, current_user=current_user
            )

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertTrue("file" in ctx.exception.detail[0]["loc"])

    async def test_userpic_upload_wrong_user(self):
        request, _, _ = self._make_request()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = MagicMock()
        current_user.id = 99

        file = self._make_file(filename="x.png", content_type="image/png")

        with self.assertRaises(E) as ctx:
            await userpic_upload(
                1, request, file=file, session=session, cache=cache, current_user=current_user
            )

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertTrue("user_id" in ctx.exception.detail[0]["loc"])
