import unittest
from app.models.document_model import Document
from unittest.mock import patch, MagicMock
from app.config import get_config

cfg = get_config()


class DocumentModelTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.models.document_model.get_index")
    @patch("app.models.document_model.hash_str")
    @patch("app.models.document_model.decrypt_int")
    @patch("app.models.document_model.encrypt_int")
    @patch("app.models.document_model.decrypt_str")
    @patch("app.models.document_model.encrypt_str")
    async def test_document_init_to_dict(
            self, encrypt_str_mock, decrypt_str_mock, encrypt_int_mock,
            decrypt_int_mock, hash_str_mock, get_index_mock):
        encrypt_str_mock.side_effect = [
            "original_filename_encrypted",
            "document_filename_encrypted",
            "document_mimetype_encrypted",
            "document_summary_encrypted",
            "thumbnail_filename_encrypted",
        ]
        encrypt_int_mock.return_value = "document_filesize_encrypted"
        get_index_mock.return_value = "original_filename_index"

        document = Document(
            123, "filename.jpeg", "abcd-1234", 234, "image/jpeg",
            collection_id=345, document_summary="document summary")

        self.assertIsNone(document.id)
        self.assertIsNone(document.created_date_encrypted)
        self.assertIsNone(document.updated_date_encrypted)
        self.assertEqual(document.user_id, 123)
        self.assertEqual(document.collection_id, 345)
        self.assertEqual(document.original_filename_encrypted,
                         "original_filename_encrypted")
        self.assertEqual(document.document_filename_encrypted,
                         "document_filename_encrypted")
        self.assertEqual(document.document_filesize_encrypted,
                         "document_filesize_encrypted")
        self.assertEqual(document.document_mimetype_encrypted,
                         "document_mimetype_encrypted")
        self.assertEqual(document.document_summary_encrypted,
                         "document_summary_encrypted")

        user_mock = MagicMock(id=123, username="username")
        document.document_user = user_mock

        collection_mock = MagicMock(id=345, collection_name="collection name")
        document.document_collection = collection_mock

        document.id = 456

        decrypt_str_mock.side_effect = [
            "filename.jpeg", "image/jpeg", "document summary",
            "document_filename", "thumbnail_filename"
        ]
        decrypt_int_mock.side_effect = [
            "created_date", "updated_date", 234
        ]
        to_dict = await document.to_dict()

        self.assertDictEqual(to_dict, {
            "id": 456,
            "created_date": "created_date",
            "updated_date": "updated_date",
            "user_id": 123,
            "username": "username",
            "collection_id": 345,
            "collection_name": "collection name",
            "original_filename": "filename.jpeg",
            "document_filesize": 234,
            "document_mimetype": "image/jpeg",
            "document_summary": "document summary",
            "document_tags": [],
            "document_url": cfg.DOCUMENTS_URL + "document_filename",
            "thumbnail_url": cfg.THUMBNAILS_URL + "thumbnail_filename",
            "document_meta": {},
        })


if __name__ == "__main__":
    unittest.main()
