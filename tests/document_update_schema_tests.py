import unittest
from pydantic import ValidationError
from app.schemas.document_update import (
    DocumentUpdateRequest, DocumentUpdateResponse)


class CollectionUpdateSchemaTest(unittest.TestCase):

    def test_request_correct(self):
        res = DocumentUpdateRequest(collection_id=42, filename="dummy.jpeg")
        self.assertEqual(res.collection_id, 42)
        self.assertEqual(res.filename, "dummy.jpeg")
        self.assertIsNone(res.summary)

    def test_request_collection_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(filename="dummy.jpeg")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_collection_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(collection_id=None, filename="dummy.jpeg")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_collection_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(
                collection_id="not-int", filename="dummy.jpeg")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_collection_id_integer_0(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(collection_id=0, filename="dummy.jpeg")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_readonly_coercion_integer_1(self):
        res = DocumentUpdateRequest(collection_id=1, filename="dummy.jpeg")
        self.assertEqual(res.collection_id, 1)

    def test_request_collection_id_coercion(self):
        res = DocumentUpdateRequest(collection_id="42", filename="dummy.jpeg")
        self.assertEqual(res.collection_id, 42)

    def test_request_filename_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(collection_id=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filename",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_filename_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(collection_id=42, filename=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filename",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_filename_string_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(collection_id=42, filename="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filename",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_filename_string_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(collection_id=42, filename="X" * 256)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filename",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_filename_string_shortest(self):
        res = DocumentUpdateRequest(collection_id=42, filename="X")
        self.assertEqual(res.filename, "X")

    def test_request_filename_string_longest(self):
        res = DocumentUpdateRequest(collection_id=42, filename="X" * 255)
        self.assertEqual(res.filename, "X" * 255)

    def test_request_filename_string_stripped(self):
        res = DocumentUpdateRequest(collection_id=42, filename=" X ")
        self.assertEqual(res.filename, "X")

    def test_request_summary_none(self):
        res = DocumentUpdateRequest(
            collection_id=42, filename="dummy.jpeg", summary=None)
        self.assertIsNone(res.summary)

    def test_request_summary_string_empty(self):
        res = DocumentUpdateRequest(
            collection_id=42, filename="dummy.jpeg", summary="")
        self.assertIsNone(res.summary)

    def test_request_summary_string_longest(self):
        res = DocumentUpdateRequest(
            collection_id=42, filename="dummy.jpeg", summary="X" * 4096)
        self.assertEqual(res.summary, "X" * 4096)

    def test_request_summary_string_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(
                collection_id=42, filename="dummy.jpeg", summary="X" * 4097)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_summary_integer(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(
                collection_id=42, filename="dummy.jpeg", summary=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_summary_string_stripped(self):
        res = DocumentUpdateRequest(
            collection_id=42, filename="dummy.jpeg", summary=" X ")
        self.assertEqual(res.summary, "X")

    def test_request_extra_forbidden(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateRequest(
                collection_id=42, filename="dummy.jpeg", foo="bar")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("foo",))
        self.assertEqual(e.get("type"), "extra_forbidden")

    def test_response_correct(self):
        res = DocumentUpdateResponse(
            document_id=123, latest_revision_number=42)
        self.assertEqual(res.document_id, 123)

    def test_response_document_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateResponse(latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_document_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateResponse(
                document_id=None, latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_document_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateResponse(
                document_id="not-int", latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("document_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_document_id_coercion(self):
        res = DocumentUpdateResponse(
            document_id="123", latest_revision_number=42)
        self.assertEqual(res.document_id, 123)

    def test_response_latest_revision_number_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateResponse(document_id=123)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_latest_revision_number_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateResponse(
                document_id=123, latest_revision_number=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_latest_revision_number_string(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentUpdateResponse(
                document_id=123, latest_revision_number="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_latest_revision_number_coercion(self):
        res = DocumentUpdateResponse(
            document_id=123, latest_revision_number="42")
        self.assertEqual(res.latest_revision_number, 42)
