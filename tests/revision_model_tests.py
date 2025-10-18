import os
import unittest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from app.models.file_revision import FileRevision


class RevisionModelTest(unittest.IsolatedAsyncioTestCase):

    def test_init(self):
        user_id = 42
        file_id = 37
        revision_number = 2
        uuid = "9c5b94b1"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        revision = FileRevision(
            user_id, file_id, revision_number,
            uuid, filesize, checksum)

        self.assertEqual(revision.user_id, user_id)
        self.assertEqual(revision.file_id, file_id)
        self.assertEqual(revision.revision_number, revision_number)
        self.assertEqual(revision.uuid, uuid)
        self.assertEqual(revision.filesize, filesize)
        self.assertEqual(revision.checksum, checksum)

        self.assertIsNone(revision.id)
        self.assertIsNone(revision.created_date)
        self.assertIsNone(revision.revision_user)
        self.assertIsNone(revision.revision_file)

        self.assertFalse(revision._cacheable)
        self.assertEqual(revision.__tablename__, "files_revisions")

    async def test_to_dict(self):
        user_id = 42
        file_id = 37
        revision_number = 2
        uuid = "9c5b94b1"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        user_mock = AsyncMock()
        file_mock = AsyncMock()

        revision = FileRevision(
            user_id, file_id, revision_number,
            uuid, filesize, checksum)

        revision.revision_user = user_mock
        revision.revision_file = file_mock
        revision.id = 12
        revision.created_date = "created-date"

        res = await revision.to_dict()
        self.assertDictEqual(res, {
            "id": 12,
            "user": user_mock.to_dict.return_value,
            "file_id": file_id,
            "created_date": "created-date",
            "revision_number": revision_number,
            "uuid": uuid,
            "filesize": filesize,
            "checksum": checksum,
        })

    def test_path_for_uuid(self):
        config = SimpleNamespace(REVISIONS_DIR="/tmp/data")
        uuid = "9c5b94b1"
        expected = os.path.join(config.REVISIONS_DIR, uuid)
        self.assertEqual(FileRevision.path_for_uuid(
            config, uuid), expected)

    def test_path(self):
        config = SimpleNamespace(REVISIONS_DIR="/tmp/data")
        revision = FileRevision(
            42, 37, 1, "9c5b94b1", 10500, "3f6cdcb77bbd")
        expected = os.path.join(
            config.REVISIONS_DIR, "9c5b94b1")
        self.assertEqual(revision.path(config), expected)
