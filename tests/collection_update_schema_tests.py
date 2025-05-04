import unittest
from pydantic import ValidationError
from app.schemas.collection_update_schema import CollectionUpdateRequest


class CollectionUpdateSchemaTest(unittest.TestCase):

    def test_collection_name_empty(self):
        data = {
            "collection_name": "",
            "collection_summary": "lorem ipsum",
        }
        with self.assertRaises(ValidationError):
            CollectionUpdateRequest(**data)

    def test_collection_name_too_long(self):
        data = {
            "collection_name": "a" * 80,
            "collection_summary": "lorem ipsum",
        }
        with self.assertRaises(ValidationError):
            CollectionUpdateRequest(**data)

    def test_collection_name_lengh_min(self):
        data = {
            "collection_name": "aa",
            "collection_summary": "lorem ipsum",
        }
        res = CollectionUpdateRequest(**data)
        self.assertEqual(res.collection_name, "aa")

    def test_collection_name_lengh_max(self):
        data = {
            "collection_name": "a" * 79,
            "collection_summary": "lorem ipsum",
        }
        res = CollectionUpdateRequest(**data)
        self.assertEqual(res.collection_name, "a" * 79)

    def test_collection_name_strip(self):
        data = {
            "collection_name": "  dummy  ",
            "collection_summary": "lorem ipsum",
        }
        res = CollectionUpdateRequest(**data)
        self.assertEqual(res.collection_name, "dummy")

    def test_collection_summary_none(self):
        data = {
            "collection_name": "dummy",
            "collection_summary": None,
        }
        res = CollectionUpdateRequest(**data)
        self.assertEqual(res.collection_summary, None)

    def test_collection_summary_empty(self):
        data = {
            "collection_name": "dummy",
            "collection_summary": "",
        }
        res = CollectionUpdateRequest(**data)
        self.assertEqual(res.collection_summary, None)

    def test_collection_summary_too_long(self):
        data = {
            "collection_name": "dummy",
            "collection_summary": "a" * 4096,
        }
        with self.assertRaises(ValidationError):
            CollectionUpdateRequest(**data)

    def test_collection_summary_length_max(self):
        data = {
            "collection_name": "dummy",
            "collection_summary": "a" * 4095,
        }
        res = CollectionUpdateRequest(**data)
        self.assertEqual(res.collection_summary, "a" * 4095)

    def test_collection_summary_strip(self):
        data = {
            "collection_name": "dummy",
            "collection_summary": "  dummy  ",
        }
        res = CollectionUpdateRequest(**data)
        self.assertEqual(res.collection_summary, "dummy")


if __name__ == "__main__":
    unittest.main()
