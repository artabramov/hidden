import unittest
from pydantic import ValidationError
from app.schemas.document_update_schema import DocumentUpdateRequest


class DocumentUpdateSchemaTest(unittest.TestCase):

    def test_original_filename_empty(self):
        data = {
            "original_filename": "",
        }
        with self.assertRaises(ValidationError):
            DocumentUpdateRequest(**data)

    def test_original_filename_too_long(self):
        data = {
            "original_filename": "a" * 256,
        }
        with self.assertRaises(ValidationError):
            DocumentUpdateRequest(**data)

    def test_original_filename_len_min(self):
        data = {
            "original_filename": "a",
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "a")

    def test_original_filename_len_max(self):
        data = {
            "original_filename": "a" * 255,
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "a" * 255)

    def test_document_summary_none(self):
        data = {
            "original_filename": "filename",
            "document_summary": None,
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "filename")
        self.assertIsNone(schema.document_summary)

    def test_document_summary_empty(self):
        data = {
            "original_filename": "filename",
            "document_summary": "",
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "filename")
        self.assertIsNone(schema.document_summary)

    def test_document_summary_len_min(self):
        data = {
            "original_filename": "filename",
            "document_summary": "a",
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "filename")
        self.assertEqual(schema.document_summary, "a")

    def test_document_summary_len_max(self):
        data = {
            "original_filename": "filename",
            "document_summary": "a" * 4095,
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "filename")
        self.assertEqual(schema.document_summary, "a" * 4095)

    def test_document_summary_strip(self):
        data = {
            "original_filename": "filename",
            "document_summary": "  summary  ",
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "filename")
        self.assertEqual(schema.document_summary, "summary")

    def test_document_summary_len_exceeded(self):
        data = {
            "original_filename": "filename",
            "document_summary": "a" * 4096,
        }
        with self.assertRaises(ValidationError):
            DocumentUpdateRequest(**data)

    def test_collection_none(self):
        data = {
            "original_filename": "filename",
            "collection_id": None,
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "filename")
        self.assertIsNone(schema.collection_id)

    def test_collection_int(self):
        data = {
            "original_filename": "filename",
            "collection_id": 123,
        }
        schema = DocumentUpdateRequest(**data)
        self.assertEqual(schema.original_filename, "filename")
        self.assertEqual(schema.collection_id, 123)


if __name__ == "__main__":
    unittest.main()
