import unittest
from app.models.collection_model import Collection
from unittest.mock import patch, call, MagicMock
from app.config import get_config
from app.models.document_model import Document  # noqa F401
from app.models.tag_model import Tag  # noqa F401
from app.models.setting_model import Setting  # noqa F401

cfg = get_config()


class CollectionModelTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.models.collection_model.decrypt_str")
    @patch("app.models.collection_model.decrypt_int")
    @patch("app.models.collection_model.get_index")
    @patch("app.models.collection_model.hash_str")
    @patch("app.models.collection_model.encrypt_str")
    async def test_collection_init_to_dict(
            self, encrypt_str_mock, hash_str_mock, get_index_mock,
            decrypt_int_mock, decrypt_str_mock):
        encrypt_str_mock.side_effect = [
            "collection_name_encrypted",
            "collection_summary_encrypted",
            None
        ]
        decrypt_str_mock.side_effect = [
            "collection name", "collection summary", None
        ]
        decrypt_int_mock.side_effect = [
            "created_date", "updated_date"
        ]
        hash_str_mock.return_value = "collection_name_hash"
        get_index_mock.return_value = "collection_name_index"

        collection = Collection(234, "collection name", "collection summary")

        self.assertIsNone(collection.id)
        self.assertIsNone(collection.created_date_encrypted)
        self.assertIsNone(collection.updated_date_encrypted)
        self.assertEqual(collection.user_id, 234)
        self.assertEqual(collection.collection_name_encrypted,
                         "collection_name_encrypted")
        self.assertEqual(collection.collection_name_hash,
                         "collection_name_hash")
        self.assertEqual(collection.collection_name_index,
                         "collection_name_index")
        self.assertEqual(collection.collection_summary_encrypted,
                         "collection_summary_encrypted")

        self.assertListEqual(encrypt_str_mock.call_args_list, [
            call("collection name"), call("collection summary"), call(None)
        ])
        hash_str_mock.assert_called_with("collection name")
        get_index_mock.assert_called_with("collection name")

        collection.id = 123
        collection.collection_user = MagicMock(id=234, username="johndoe")

        to_dict = await collection.to_dict()
        self.assertDictEqual(to_dict, {
            "id": 123,
            "created_date": "created_date",
            "updated_date": "updated_date",
            "user_id": 234,
            "username": "johndoe",
            "collection_name": "collection name",
            "collection_summary": "collection summary",
            "thumbnail_filename": None,
            "documents_count": None,
            "collection_meta": {},
        })


if __name__ == "__main__":
    unittest.main()
