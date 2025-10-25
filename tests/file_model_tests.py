import os
import unittest
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace
from app.models.file import File


class FileModelTest(unittest.IsolatedAsyncioTestCase):

    def test_init(self):
        user_id = 42
        folder_id = 37
        filename = "myfile.jpeg"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        mimetype = "image/jpeg"
        flagged = True
        summary = "Some text"
        latest_revision_number = 1
        file = File(
            user_id, folder_id, filename, filesize, checksum,
            mimetype, flagged, summary, latest_revision_number)

        self.assertEqual(file.user_id, user_id)
        self.assertEqual(file.folder_id, folder_id)
        self.assertEqual(file.filename, filename)
        self.assertEqual(file.filesize, filesize)
        self.assertEqual(file.checksum, checksum)
        self.assertEqual(file.mimetype, mimetype)
        self.assertEqual(file.flagged, flagged)
        self.assertEqual(file.summary, summary)
        self.assertEqual(file.latest_revision_number,
                         latest_revision_number)

        self.assertIsNone(file.id)
        self.assertIsNone(file.created_date)
        self.assertIsNone(file.updated_date)
        self.assertIsNone(file.file_user)
        self.assertIsNone(file.file_folder)
        self.assertIsNone(file.file_thumbnail)
        self.assertListEqual(file.file_meta, [])
        self.assertListEqual(file.file_tags, [])
        self.assertListEqual(file.file_revisions, [])

        self.assertTrue(file._cacheable)
        self.assertEqual(file.__tablename__, "files")

    async def test_to_dict(self):
        user_id = 42
        folder_id = 37
        filename = "myfile.jpeg"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        mimetype = "image/jpeg"
        flagged = True
        summary = "Some text"
        latest_revision_number = 1
        user_mock = AsyncMock()
        folder_mock = AsyncMock()

        file = File(
            user_id, folder_id, filename, filesize, checksum,
            mimetype, flagged, summary=summary,
            latest_revision_number=latest_revision_number)

        file.file_user = user_mock
        file.file_folder = folder_mock
        file.id = 12
        file.created_date = "created-date"
        file.updated_date = "updated-date"

        res = await file.to_dict()
        self.assertDictEqual(res, {
            "id": 12,
            "user": user_mock.to_dict.return_value,
            "folder": folder_mock.to_dict.return_value,
            "created_date": "created-date",
            "updated_date": "updated-date",
            "flagged": flagged,
            "filename": filename,
            "filesize": filesize,
            "mimetype": mimetype,
            "checksum": checksum,
            "summary": summary,
            "latest_revision_number": latest_revision_number,
            "has_thumbnail": False,
            "file_revisions": [],
            "file_tags": [],
        })

    def test_path_for_filename(self):
        config = SimpleNamespace(FILES_DIR="/tmp/data")
        folder_name = "dummies"
        filename = "dummy.jpeg"
        expected = os.path.join(
            config.FILES_DIR, folder_name, filename)
        self.assertEqual(File.path_for_filename(
            config, folder_name, filename), expected)

    def test_path(self):
        config = SimpleNamespace(FILES_DIR="/tmp/data")
        file = File(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        file.file_folder = MagicMock()
        file.file_folder.name = "dummies"
        expected = os.path.join(
            config.FILES_DIR, "dummies", "dummies.jpeg")
        self.assertEqual(file.path(config), expected)

    def test_has_thumbnail_true(self):
        file = File(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        file.file_thumbnail = MagicMock()
        self.assertTrue(file.has_thumbnail)

    def test_has_thumbnail_false(self):
        file = File(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        file.file_thumbnail = None
        self.assertFalse(file.has_thumbnail)

    def test_has_revisions_true(self):
        file = File(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        file.file_revisions = [MagicMock()]
        self.assertTrue(file.has_revisions)

    def test_has_revisions_false(self):
        file = File(
            42, 37, "dummies.jpeg", 10500, "3f6cdcb77bbd",
            "image/jpeg", True)
        file.file_revisions = []
        self.assertFalse(file.has_revisions)
