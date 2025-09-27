import unittest
from pydantic import ValidationError
from app.schemas.document_upload import DocumentUploadResponse


class DocumentUploadSchemaTest(unittest.TestCase):

    def test_response_correct(self):
        res = DocumentUploadResponse(
            document_id=123, latest_revision_number=42)
        self.assertEqual(res.document_id, 123)
        self.assertEqual(res.latest_revision_number, 42)

    def test_response_document_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUploadResponse(latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_document_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUploadResponse(
                document_id=None, latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_document_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUploadResponse(
                document_id="not-int", latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_document_id_coercion(self):
        res = DocumentUploadResponse(
            document_id="123", latest_revision_number=42)
        self.assertEqual(res.document_id, 123)

    def test_response_latest_revision_number_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUploadResponse(document_id=123)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_latest_revision_number_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUploadResponse(
                document_id=123, latest_revision_number=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_latest_revision_number_string(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUploadResponse(
                document_id=123, latest_revision_number="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_latest_revision_number_coercion(self):
        res = DocumentUploadResponse(
            document_id=123, latest_revision_number="42")
        self.assertEqual(res.latest_revision_number, 42)
