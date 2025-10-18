import os
import unittest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from app.models.folder import Folder
from app.models.file import File  # noqa: F401


class FolderModelTest(unittest.IsolatedAsyncioTestCase):

    def test_init(self):
        user_id = 42
        readonly = True
        name = "Dummy"
        summary = "Some text"
        folder = Folder(user_id, readonly, name, summary)

        self.assertEqual(folder.user_id, user_id)
        self.assertEqual(folder.readonly, readonly)
        self.assertEqual(folder.name, name)
        self.assertEqual(folder.summary, summary)

        self.assertIsNone(folder.id)
        self.assertIsNone(folder.created_date)
        self.assertIsNone(folder.updated_date)
        self.assertIsNone(folder.folder_user)
        self.assertListEqual(folder.folder_meta, [])
        self.assertListEqual(folder.folder_files, [])

        self.assertTrue(folder._cacheable)
        self.assertEqual(folder.__tablename__, "folders")

    async def test_to_dict(self):
        user_mock = AsyncMock()
        folder = Folder(42, True, "dummy", "some text")
        folder.folder_user = user_mock
        folder.id = 37
        folder.created_date = "created-date"
        folder.updated_date = "updated-date"

        res = await folder.to_dict()
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
        config = SimpleNamespace(FILES_DIR="/tmp/data")
        name = "dummies"
        expected = os.path.join(config.FILES_DIR, name)
        self.assertEqual(Folder.path_for_dir(config, name), expected)

    def test_path(self):
        config = SimpleNamespace(FILES_DIR="/tmp/data")
        folder = Folder(user_id=1, readonly=False, name="dummies")
        expected = os.path.join(config.FILES_DIR, "dummies")
        self.assertEqual(folder.path(config), expected)
