import unittest
from pydantic import ValidationError
from app.schemas.tag_insert_schema import TagInsertRequest


class TagInsertSchemaTest(unittest.TestCase):

    def test_tag_insert_schema_value_none(self):
        with self.assertRaises(ValidationError):
            TagInsertRequest(tag_value=None)

    def test_tag_insert_schema_value_empty(self):
        with self.assertRaises(ValidationError):
            TagInsertRequest(tag_value="")

    def test_tag_insert_schema_value_len_too_long(self):
        with self.assertRaises(ValidationError):
            TagInsertRequest(tag_value="a" * 48)

    def test_tag_insert_schema_value_len_min(self):
        schema = TagInsertRequest(tag_value="a")
        self.assertEqual(schema.tag_value, "a")

    def test_tag_insert_schema_value_len_max(self):
        schema = TagInsertRequest(tag_value="a" * 47)
        self.assertEqual(schema.tag_value, "a" * 47)

    def test_tag_insert_schema_value_strip(self):
        schema = TagInsertRequest(tag_value="  a  ")
        self.assertEqual(schema.tag_value, "a")

    def test_tag_insert_schema_value_lower(self):
        schema = TagInsertRequest(tag_value="ABC")
        self.assertEqual(schema.tag_value, "abc")


if __name__ == "__main__":
    unittest.main()
