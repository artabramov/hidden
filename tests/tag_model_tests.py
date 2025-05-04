import unittest
from app.models.tag_model import Tag
from unittest.mock import patch
from app.config import get_config

cfg = get_config()


class TagModelTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.models.tag_model.hash_str")
    @patch("app.models.tag_model.decrypt_str")
    @patch("app.models.tag_model.encrypt_str")
    async def test_tag_init(self, encrypt_str_mock, decrypt_str_mock,
                            hash_str_mock):
        encrypt_str_mock.return_value = "tag_value_encrypted"
        decrypt_str_mock.return_value = "tag_value"
        hash_str_mock.return_value = "tag_value_hash"

        tag = Tag(123, "tag_value")

        self.assertEqual(tag.document_id, 123)
        self.assertEqual(tag.tag_value, "tag_value")
        self.assertEqual(tag.tag_value_encrypted, "tag_value_encrypted")
        self.assertEqual(tag.tag_value_hash, "tag_value_hash")


if __name__ == "__main__":
    unittest.main()
