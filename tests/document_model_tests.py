import unittest
from app.models.document_model import Document
from unittest.mock import patch, MagicMock
from app.config import get_config

cfg = get_config()


class DocumentModelTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.models.document_model.get_index")
    @patch("app.models.document_model.decrypt_int")
    @patch("app.models.document_model.encrypt_int")
    @patch("app.models.document_model.decrypt_str")
    @patch("app.models.document_model.encrypt_str")
    async def test_document_init_to_dict(
        self, encrypt_str_mock, decrypt_str_mock, encrypt_int_mock,
        decrypt_int_mock, get_index_mock
    ):
        encrypt_str_mock.side_effect = [
            "original_filename_encrypted",
            "document_mimetype_encrypted",
            "document_summary_encrypted",
            "thumbnail_filename_encrypted",
        ]
        encrypt_int_mock.return_value = "document_filesize_encrypted"
        get_index_mock.return_value = 111

        document = Document(
            123, "filename.jpeg", "ignored-filename", 234, "image/jpeg",
            collection_id=345, document_summary="document summary",
            thumbnail_filename="thumb.jpg"
        )

        self.assertIsNone(document.id)
        self.assertEqual(document.user_id, 123)
        self.assertEqual(document.collection_id, 345)
        self.assertEqual(document.original_filename_encrypted,
                         "original_filename_encrypted")
        self.assertEqual(document.document_filesize_encrypted,
                         "document_filesize_encrypted")
        self.assertEqual(document.document_mimetype_encrypted,
                         "document_mimetype_encrypted")
        self.assertEqual(document.document_summary_encrypted,
                         "document_summary_encrypted")
        self.assertEqual(document.thumbnail_filename_encrypted,
                         "thumbnail_filename_encrypted")

        user_mock = MagicMock(id=123, username="username")
        document.document_user = user_mock

        collection_mock = MagicMock(id=345,
                                    collection_name="collection name")
        document.document_collection = collection_mock

        document.id = 456
        document.document_tags = []
        document.document_meta = []

        decrypt_str_mock.side_effect = [
            "filename.jpeg", "image/jpeg", "document summary", "thumb.jpg"
        ]
        decrypt_int_mock.side_effect = [1111111111, 2222222222, 234]

        to_dict = await document.to_dict()

        self.assertDictEqual(to_dict, {
            "id": 456,
            "created_date": 1111111111,
            "updated_date": 2222222222,
            "user_id": 123,
            "username": "username",
            "collection_id": 345,
            "collection_name": "collection name",
            "original_filename": "filename.jpeg",
            "document_filesize": 234,
            "document_mimetype": "image/jpeg",
            "document_summary": "document summary",
            "document_tags": [],
            "thumbnail_filename": "thumb.jpg",
            "document_meta": {},
        })


if __name__ == "__main__":
    unittest.main()
