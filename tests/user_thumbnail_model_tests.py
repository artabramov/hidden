import unittest
from app.models.user_thumbnail import UserThumbnail


class UserpicModelTest(unittest.IsolatedAsyncioTestCase):

    def test_init(self):
        user_id = 37
        uuid = "9c5b94b1"
        filesize = 10500
        checksum = "3f6cdcb77bbd"
        thumbnail = UserThumbnail(user_id, uuid, filesize, checksum)

        self.assertEqual(thumbnail.user_id, user_id)
        self.assertEqual(thumbnail.uuid, uuid)
        self.assertEqual(thumbnail.filesize, filesize)
        self.assertEqual(thumbnail.checksum, checksum)

        self.assertIsNone(thumbnail.id)
        self.assertIsNone(thumbnail.created_date)
        self.assertIsNone(thumbnail.updated_date)

        self.assertFalse(thumbnail._cacheable)
        self.assertEqual(thumbnail.__tablename__, "users_thumbnails")
