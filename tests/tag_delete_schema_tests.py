import unittest
from pydantic import ValidationError
from app.schemas.tag_delete_schema import TagDeleteRequest


class TagInsertSchemaTest(unittest.TestCase):

    def test_tag_delete_schema_value_none(self):
        with self.assertRaises(ValidationError):
            TagDeleteRequest(tag_value=None)

    def test_tag_delete_schema_value_empty(self):
        with self.assertRaises(ValidationError):
            TagDeleteRequest(tag_value="")

    def test_tag_delete_schema_value_len_too_long(self):
        with self.assertRaises(ValidationError):
            TagDeleteRequest(tag_value="a" * 48)

    def test_tag_delete_schema_value_len_min(self):
        schema = TagDeleteRequest(tag_value="a")
        self.assertEqual(schema.tag_value, "a")

    def test_tag_delete_schema_value_len_max(self):
        schema = TagDeleteRequest(tag_value="a" * 47)
        self.assertEqual(schema.tag_value, "a" * 47)

    def test_tag_delete_schema_value_strip(self):
        schema = TagDeleteRequest(tag_value="  a  ")
        self.assertEqual(schema.tag_value, "a")

    def test_tag_delete_schema_value_lower(self):
        schema = TagDeleteRequest(tag_value="ABC")
        self.assertEqual(schema.tag_value, "abc")


if __name__ == "__main__":
    unittest.main()
