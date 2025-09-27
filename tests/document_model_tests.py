import os
import unittest
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace
from app.models.document import Document


class DocumentModelTest(unittest.IsolatedAsyncioTestCase):

    def test_init(self):
        user_id = 42
        collection_id = 37
        filename = "myfile.jpeg"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        mimetype = "image/jpeg"
        flagged = True
        summary = "Some text"
        latest_revision_number = 1
        document = Document(
            user_id, collection_id, filename, filesize, checksum,
            mimetype, flagged, summary, latest_revision_number)

        self.assertEqual(document.user_id, user_id)
        self.assertEqual(document.collection_id, collection_id)
        self.assertEqual(document.filename, filename)
        self.assertEqual(document.filesize, filesize)
        self.assertEqual(document.checksum, checksum)
        self.assertEqual(document.mimetype, mimetype)
        self.assertEqual(document.flagged, flagged)
        self.assertEqual(document.summary, summary)
        self.assertEqual(document.latest_revision_number,
                         latest_revision_number)

        self.assertIsNone(document.id)
        self.assertIsNone(document.created_date)
        self.assertIsNone(document.updated_date)
        self.assertIsNone(document.document_user)
        self.assertIsNone(document.document_collection)
        self.assertIsNone(document.document_thumbnail)
        self.assertListEqual(document.document_meta, [])
        self.assertListEqual(document.document_tags, [])
        self.assertListEqual(document.document_revisions, [])

        self.assertTrue(document._cacheable)
        self.assertEqual(document.__tablename__, "documents")
    
    async def test_to_dict(self):
        user_id = 42
        collection_id = 37
        filename = "myfile.jpeg"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        mimetype = "image/jpeg"
        flagged = True
        summary = "Some text"
        latest_revision_number = 1
        user_mock = AsyncMock()
        collection_mock = AsyncMock()

        document = Document(
            user_id, collection_id, filename, filesize, checksum,
            mimetype, flagged, summary=summary,
            latest_revision_number=latest_revision_number)

        document.document_user = user_mock
        document.document_collection = collection_mock
        document.id = 12
        document.created_date = "created-date"
        document.updated_date = "updated-date"
        
        res = await document.to_dict()
        self.assertDictEqual(res, {
            "id": 12,
            "user": user_mock.to_dict.return_value,
            "collection": collection_mock.to_dict.return_value,
            "created_date": "created-date",
            "updated_date": "updated-date",
            "flagged": flagged,
            "filename": filename,
            "filesize": filesize,
            "mimetype": mimetype,
            "checksum": checksum,
            "summary": summary,
            "latest_revision_number": latest_revision_number,
            "document_revisions": [],
        })


    def test_path_for_filename(self):
        config = SimpleNamespace(DOCUMENTS_DIR="/tmp/data")
        collection_name = "dummies"
        filename = "dummy.jpeg"
        expected = os.path.join(
            config.DOCUMENTS_DIR, collection_name, filename)
        self.assertEqual(Document.path_for_filename(
            config, collection_name, filename), expected)

    def test_path(self):
        config = SimpleNamespace(DOCUMENTS_DIR="/tmp/data")
        document = Document(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        document.document_collection = MagicMock()
        document.document_collection.name="dummies"
        expected = os.path.join(
            config.DOCUMENTS_DIR, "dummies", "dummies.jpeg")
        self.assertEqual(document.path(config), expected)

    def test_has_thumbnail_true(self):
        document = Document(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        document.document_thumbnail = MagicMock()
        self.assertTrue(document.has_thumbnail)

    def test_has_thumbnail_false(self):
        document = Document(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        document.document_thumbnail = None
        self.assertFalse(document.has_thumbnail)

    def test_has_revisions_true(self):
        document = Document(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        document.document_revisions = [MagicMock()]
        self.assertTrue(document.has_revisions)

    def test_has_revisions_false(self):
        document = Document(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        document.document_revisions = []
        self.assertFalse(document.has_revisions)
