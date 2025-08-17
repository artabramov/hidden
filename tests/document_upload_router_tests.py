import unittest
import os
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.routers.document_upload_router import _document_upload
from app.hook import HOOK_AFTER_DOCUMENT_UPLOAD
from app.config import get_config

cfg = get_config()


class DocumentUploadRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_file_upload_error(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            video_capture_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.jpeg", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()
        uuid_mock.uuid4.side_effect = [
            "document_filename", "thumbnail_filename"]

        FileManagerMock.mimetype.return_value = "image/jpeg"
        FileManagerMock.upload.side_effect = FileNotFoundError

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(FileNotFoundError):
            await _document_upload(
                file_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "document_filename"))

        FileManagerMock.mimetype.assert_called_with(file_mock.filename)

        FileManagerMock.delete.assert_called_once_with(
            os.path.join(cfg.DOCUMENTS_PATH, "document_filename")
        )

        image_resize_mock.assert_not_called()
        video_capture_mock.assert_not_called()

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_file_copy_error(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            video_capture_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.jpeg", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        uuid_mock.uuid4.side_effect = [
            "document_filename", "thumbnail_filename"]

        FileManagerMock.mimetype.return_value = "image/jpeg"
        FileManagerMock.upload.side_effect = FileNotFoundError

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(FileNotFoundError):
            await _document_upload(
                file_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "document_filename"))

        FileManagerMock.mimetype.assert_called_with(file_mock.filename)

        FileManagerMock.delete.assert_called_once_with(
            os.path.join(cfg.DOCUMENTS_PATH, "document_filename"))

        image_resize_mock.assert_not_called()
        video_capture_mock.assert_not_called()

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_image_resize_error(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            video_capture_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.jpeg", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()
        uuid_mock.uuid4.side_effect = [
            "document_filename", "thumbnail_filename"]
        image_resize_mock.side_effect = FileNotFoundError
        FileManagerMock.mimetype.return_value = "image/jpeg"

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(FileNotFoundError):
            await _document_upload(
                file_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        FileManagerMock.mimetype.assert_called_with(
            file_mock.filename)

        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "document_filename"))

        image_resize_mock.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "thumbnail_filename"),
            cfg.THUMBNAILS_WIDTH, cfg.THUMBNAILS_HEIGHT,
            cfg.THUMBNAILS_QUALITY
        )
        video_capture_mock.assert_not_called()

        self.assertListEqual(FileManagerMock.delete.await_args_list, [
            call(os.path.join(cfg.DOCUMENTS_PATH, "document_filename")),
            call(os.path.join(cfg.THUMBNAILS_PATH, "thumbnail_filename")),
        ])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_image_read_error(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            video_capture_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.jpeg", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()
        uuid_mock.uuid4.side_effect = ["abcd-1234", "efgh-5678"]
        FileManagerMock.mimetype.return_value = "image/jpeg"
        FileManagerMock.read.side_effect = FileNotFoundError

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(FileNotFoundError):
            await _document_upload(
                file_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        FileManagerMock.mimetype.assert_called_with(
            file_mock.filename)

        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))

        image_resize_mock.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"),
            cfg.THUMBNAILS_WIDTH, cfg.THUMBNAILS_HEIGHT,
            cfg.THUMBNAILS_QUALITY
        )
        video_capture_mock.assert_not_called()

        FileManagerMock.read.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"))

        self.assertListEqual(FileManagerMock.delete.await_args_list, [
            call(os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234")),
            call(os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678")),
        ])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.encrypt_bytes")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_image_write_error(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            encrypt_bytes_mock, video_capture_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.jpeg", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()
        uuid_mock.uuid4.side_effect = ["abcd-1234", "efgh-5678"]
        FileManagerMock.mimetype.return_value = "image/jpeg"
        FileManagerMock.write.side_effect = FileNotFoundError

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(FileNotFoundError):
            await _document_upload(
                file_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        FileManagerMock.mimetype.assert_called_with(
            file_mock.filename)

        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))

        image_resize_mock.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"),
            cfg.THUMBNAILS_WIDTH, cfg.THUMBNAILS_HEIGHT,
            cfg.THUMBNAILS_QUALITY
        )
        video_capture_mock.assert_not_called()

        FileManagerMock.read.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"))

        encrypt_bytes_mock.assert_called_with(
            FileManagerMock.read.return_value)

        FileManagerMock.write.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"),
            encrypt_bytes_mock.return_value)

        self.assertListEqual(FileManagerMock.delete.await_args_list, [
            call(os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234")),
            call(os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678")),
        ])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.encrypt_bytes")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_file_read_error(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            encrypt_bytes_mock, video_capture_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.jpeg", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()
        uuid_mock.uuid4.side_effect = ["abcd-1234", "efgh-5678"]
        FileManagerMock.mimetype.return_value = "image/jpeg"
        FileManagerMock.read.side_effect = [b"data", FileNotFoundError]

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(FileNotFoundError):
            await _document_upload(
                file_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        FileManagerMock.mimetype.assert_called_with(
            file_mock.filename)

        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))

        image_resize_mock.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"),
            cfg.THUMBNAILS_WIDTH, cfg.THUMBNAILS_HEIGHT,
            cfg.THUMBNAILS_QUALITY
        )
        video_capture_mock.assert_not_called()

        self.assertListEqual(FileManagerMock.read.await_args_list, [
            call(os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678")),
            call(os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234")),
        ])

        encrypt_bytes_mock.assert_called_with(b"data")

        FileManagerMock.write.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"),
            encrypt_bytes_mock.return_value)

        self.assertListEqual(FileManagerMock.delete.await_args_list, [
            call(os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234")),
            call(os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678")),
        ])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.document_upload_router.shuffle_shards")
    @patch("app.routers.document_upload_router.CollectionLibrary")
    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.Repository")
    @patch("app.routers.document_upload_router.Document")
    @patch("app.routers.document_upload_router.encrypt_bytes")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_document_image_upload_success(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            encrypt_bytes_mock, DocumentMock, RepositoryMock,
            video_capture_mock, CollectionLibraryMock, shuffle_shards_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.jpeg", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        uuid_mock.uuid4.side_effect = ["abcd-1234", "efgh-5678"]
        encrypt_bytes_mock.side_effect = [b"img-encrypted", b"file-encrypted"]

        FileManagerMock.mimetype.return_value = "image/jpeg"
        FileManagerMock.read.side_effect = [b"data", b"image"]

        collection_repository_mock = AsyncMock()
        document_repository_mock = AsyncMock()
        shard_repository_mock = AsyncMock()
        RepositoryMock.side_effect = [
            collection_repository_mock, document_repository_mock,
            shard_repository_mock]

        collection_library_mock = AsyncMock()
        CollectionLibraryMock.return_value = collection_library_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        DocumentMock.return_value.id = 1

        result = await _document_upload(
            file_mock, request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock, collection_id=123)

        self.assertDictEqual(result, {"document_id": 1})

        FileManagerMock.mimetype.assert_called_with(file_mock.filename)
        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))

        image_resize_mock.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"),
            cfg.THUMBNAILS_WIDTH, cfg.THUMBNAILS_HEIGHT,
            cfg.THUMBNAILS_QUALITY
        )
        video_capture_mock.assert_not_called()

        self.assertListEqual(FileManagerMock.read.await_args_list, [
            call(os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678")),
            call(os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))])

        self.assertListEqual(encrypt_bytes_mock.call_args_list, [
            call(b"data"), call(b"image")])

        FileManagerMock.split.assert_called_with(
            b"file-encrypted", cfg.DOCUMENTS_PATH)
        FileManagerMock.delete.assert_called_with(
            os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))

        document_repository_mock.insert.assert_called_with(
            DocumentMock.return_value)
        collection_repository_mock.select.assert_called_with(id=123)

        CollectionLibraryMock.assert_called_with(session_mock, cache_mock)
        collection_library_mock.create_thumbnail.assert_called_with(123)

        shuffle_shards_mock.assert_called_with(
            session_mock, cache_mock
        )

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(
            HOOK_AFTER_DOCUMENT_UPLOAD, DocumentMock.return_value)

    @patch("app.routers.document_upload_router.shuffle_shards")
    @patch("app.routers.document_upload_router.video_capture")
    @patch("app.routers.document_upload_router.Repository")
    @patch("app.routers.document_upload_router.Document")
    @patch("app.routers.document_upload_router.encrypt_bytes")
    @patch("app.routers.document_upload_router.image_resize")
    @patch("app.routers.document_upload_router.uuid")
    @patch("app.routers.document_upload_router.Hook")
    @patch("app.routers.document_upload_router.FileManager", new_callable=AsyncMock)  # noqa E501
    async def test_document_video_upload_success(
            self, FileManagerMock, HookMock, uuid_mock, image_resize_mock,
            encrypt_bytes_mock, DocumentMock, RepositoryMock,
            video_capture_mock, shuffle_shards_mock):
        request_mock = MagicMock()
        file_mock = AsyncMock(filename="dummy.mp4", size=1234)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        uuid_mock.uuid4.side_effect = ["abcd-1234", "efgh-5678"]
        encrypt_bytes_mock.side_effect = [b"img-encrypted", b"file-encrypted"]

        FileManagerMock.mimetype.return_value = "video/mp4"
        FileManagerMock.read.side_effect = [b"data", b"image"]

        document_repository_mock = AsyncMock()
        shard_repository_mock = AsyncMock()
        RepositoryMock.side_effect = [
            document_repository_mock, shard_repository_mock]

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await _document_upload(
                file_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertDictEqual(result, {
            "document_id": DocumentMock.return_value.id})

        FileManagerMock.mimetype.assert_called_with(
            file_mock.filename)

        FileManagerMock.upload.assert_called_with(
            file_mock, os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))

        image_resize_mock.assert_called_with(
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678"),
            cfg.THUMBNAILS_WIDTH, cfg.THUMBNAILS_HEIGHT,
            cfg.THUMBNAILS_QUALITY
        )
        video_capture_mock.assert_called_with(
            os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"),
            os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678")
        )

        self.assertListEqual(FileManagerMock.read.await_args_list, [
            call(os.path.join(cfg.THUMBNAILS_PATH, "efgh-5678")),
            call(os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234")),
        ])

        self.assertListEqual(encrypt_bytes_mock.call_args_list, [
            call(b"data"), call(b"image"),
        ])

        FileManagerMock.split.assert_called_with(
            b"file-encrypted", cfg.DOCUMENTS_PATH)
        FileManagerMock.delete.assert_called_with(
            os.path.join(cfg.DOCUMENTS_PATH, "abcd-1234"))

        document_repository_mock.insert.assert_called_with(
            DocumentMock.return_value)

        shuffle_shards_mock.assert_called_with(
            session_mock, cache_mock
        )

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(
            HOOK_AFTER_DOCUMENT_UPLOAD, DocumentMock.return_value)


if __name__ == "__main__":
    unittest.main()
