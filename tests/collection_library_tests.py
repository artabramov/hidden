import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.libraries.collection_library import CollectionLibrary
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.config import get_config

cfg = get_config()


class CollectionLibraryTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.libraries.collection_library.decrypt_bytes")
    @patch("app.libraries.collection_library.encrypt_bytes")
    @patch("app.libraries.collection_library.images_merge")
    @patch("app.libraries.collection_library.FileManager", new_callable=AsyncMock)  # noqa E501
    @patch("app.libraries.collection_library.Repository")
    async def test_create_thumbnail(self, RepositoryMock, FileManagerMock,
                                    images_merge_mock, encrypt_bytes_mock,
                                    decrypt_bytes_mock):
        session_mock = MagicMock()
        cache_mock = MagicMock()

        collection_repository_mock = AsyncMock()
        document_repository_mock = AsyncMock()
        RepositoryMock.side_effect = [
            collection_repository_mock, document_repository_mock]

        collection_mock = MagicMock(thumbnail_path="path/collection")
        collection_mock.id = 123
        collection_mock.thumbnail_filename = "old_thumb.png"
        collection_repository_mock.select.return_value = collection_mock

        doc1 = MagicMock(thumbnail_path="path/doc1.png", has_thumbnail=True)
        doc2 = MagicMock(thumbnail_path="path/doc2.png", has_thumbnail=True)
        document_repository_mock.select_all.return_value = [doc1, doc2]

        FileManagerMock.read.side_effect = [b'encrypted1', b'encrypted2']
        decrypt_bytes_mock.side_effect = [b'data1', b'data2']
        images_merge_mock.return_value = b'merged_image_data'
        encrypt_bytes_mock.return_value = b'encrypted_data'

        collection_library = CollectionLibrary(session_mock, cache_mock)
        await collection_library.create_thumbnail(collection_mock.id)

        RepositoryMock.assert_has_calls([
            call(session_mock, cache_mock, Collection),
            call(session_mock, cache_mock, Document)
        ])

        collection_repository_mock.select.assert_awaited_once_with(
            id__eq=collection_mock.id)

        document_repository_mock.select_all.assert_called_once_with(
            thumbnail_filename_encrypted__ne=None,
            collection_id__eq=collection_mock.id,
            order_by="id", order="asc", offset=0, limit=2)

        self.assertEqual(FileManagerMock.read.await_count, 2)
        FileManagerMock.read.assert_has_awaits([
            call(doc1.thumbnail_path),
            call(doc2.thumbnail_path)
        ])
        decrypt_bytes_mock.assert_has_calls([
            call(b'encrypted1'),
            call(b'encrypted2')
        ])

        images_merge_mock.assert_called_once_with(
            [b'data1', b'data2'],
            cfg.THUMBNAILS_WIDTH,
            cfg.THUMBNAILS_HEIGHT,
            cfg.THUMBNAILS_QUALITY)
        encrypt_bytes_mock.assert_called_once_with(b'merged_image_data')

        FileManagerMock.write.assert_awaited_once()
        written_path, written_data = FileManagerMock.write.call_args.args
        self.assertTrue(written_path.startswith(cfg.THUMBNAILS_PATH))
        self.assertEqual(written_data, b'encrypted_data')

        FileManagerMock.delete.assert_awaited_once_with(
            collection_mock.thumbnail_path)

        self.assertEqual(collection_repository_mock.update.await_count, 2)
        collection_repository_mock.update.assert_has_awaits([
            call(collection_mock),
            call(collection_mock)
        ])


if __name__ == "__main__":
    unittest.main()
