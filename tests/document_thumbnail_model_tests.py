import unittest
from app.models.document_thumbnail import DocumentThumbnail


class ThumbnailModelTest(unittest.IsolatedAsyncioTestCase):

    def test_init(self):
        document_id = 37
        uuid = "9c5b94b1"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        thumbnail = DocumentThumbnail(document_id, uuid, filesize, checksum)

        self.assertEqual(thumbnail.document_id, document_id)
        self.assertEqual(thumbnail.uuid, uuid)
        self.assertEqual(thumbnail.filesize, filesize)
        self.assertEqual(thumbnail.checksum, checksum)

        self.assertIsNone(thumbnail.id)
        self.assertIsNone(thumbnail.created_date)
        self.assertIsNone(thumbnail.updated_date)

        self.assertFalse(thumbnail._cacheable)
        self.assertEqual(thumbnail.__tablename__, "documents_thumbnails")
