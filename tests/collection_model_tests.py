import os
import unittest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from app.models.collection import Collection
from app.models.document import Document  # noqa: F401


class CollectionModelTest(unittest.IsolatedAsyncioTestCase):

    def test_init(self):
        user_id = 42
        readonly = True
        name = "Dummy"
        summary = "Some text"
        collection = Collection(user_id, readonly, name, summary)

        self.assertEqual(collection.user_id, user_id)
        self.assertEqual(collection.readonly, readonly)
        self.assertEqual(collection.name, name)
        self.assertEqual(collection.summary, summary)

        self.assertIsNone(collection.id)
        self.assertIsNone(collection.created_date)
        self.assertIsNone(collection.updated_date)
        self.assertIsNone(collection.collection_user)
        self.assertListEqual(collection.collection_meta, [])
        self.assertListEqual(collection.collection_documents, [])

        self.assertTrue(collection._cacheable)
        self.assertEqual(collection.__tablename__, "collections")
    
    async def test_to_dict(self):
        user_mock = AsyncMock()
        collection = Collection(42, True, "dummy", "some text")
        collection.collection_user = user_mock
        collection.id = 37
        collection.created_date = "created-date"
        collection.updated_date = "updated-date"
        
        res = await collection.to_dict()
        self.assertDictEqual(res, {
            "id": 37,
            "user": user_mock.to_dict.return_value,
            "created_date": "created-date",
            "updated_date": "updated-date",
            "readonly": True,
            "name": "dummy",
            "summary": "some text",
        })


    def test_path_for_dir(self):
        config = SimpleNamespace(DOCUMENTS_DIR="/tmp/data")
        name = "dummies"
        expected = os.path.join(config.DOCUMENTS_DIR, name)
        self.assertEqual(Collection.path_for_dir(config, name), expected)

    def test_path(self):
        config = SimpleNamespace(DOCUMENTS_DIR="/tmp/data")
        collection = Collection(user_id=1, readonly=False, name="dummies")
        expected = os.path.join(config.DOCUMENTS_DIR, "dummies")
        self.assertEqual(collection.path(config), expected)
