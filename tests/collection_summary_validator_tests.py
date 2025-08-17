import unittest
from app.validators.collection_summary_validator import (
    collection_summary_validate)


class CollectionSummaryValidatorTest(unittest.TestCase):

    def test_collection_summary_none(self):
        collection_summary = collection_summary_validate(None)
        self.assertIsNone(collection_summary)

    def test_collection_summary_empty(self):
        collection_summary = collection_summary_validate("")
        self.assertIsNone(collection_summary)

    def test_collection_summary_whitespaces(self):
        collection_summary = collection_summary_validate(" ")
        self.assertIsNone(collection_summary)

    def test_collection_summary_str(self):
        collection_summary = collection_summary_validate(" Text ")
        self.assertEqual(collection_summary, "Text")


if __name__ == "__main__":
    unittest.main()
