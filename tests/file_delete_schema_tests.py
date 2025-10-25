import unittest
from pydantic import ValidationError
from app.schemas.file_delete import FileDeleteResponse


class FileDeleteSchemaTest(unittest.TestCase):

    def test_response_correct(self):
        res = FileDeleteResponse(
            file_id=123, latest_revision_number=42)
        self.assertEqual(res.file_id, 123)
        self.assertEqual(res.latest_revision_number, 42)

    def test_response_file_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileDeleteResponse(latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("file_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_file_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileDeleteResponse(
                file_id=None, latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("file_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_file_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            FileDeleteResponse(
                file_id="not-int", latest_revision_number=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("file_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_file_id_coercion(self):
        res = FileDeleteResponse(
            file_id="123", latest_revision_number=42)
        self.assertEqual(res.file_id, 123)

    def test_response_latest_revision_number_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileDeleteResponse(file_id=123)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_latest_revision_number_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileDeleteResponse(
                file_id=123, latest_revision_number=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_latest_revision_number_string(self):
        with self.assertRaises(ValidationError) as ctx:
            FileDeleteResponse(
                file_id=123, latest_revision_number="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("latest_revision_number",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_latest_revision_number_coercion(self):
        res = FileDeleteResponse(
            file_id=123, latest_revision_number="42")
        self.assertEqual(res.latest_revision_number, 42)
