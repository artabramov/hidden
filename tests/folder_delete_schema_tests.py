import unittest
from pydantic import ValidationError
from app.schemas.folder_delete import FolderDeleteResponse


class FolderDeleteSchemaTest(unittest.TestCase):

    def test_response_correct(self):
        res = FolderDeleteResponse(folder_id="123")
        self.assertEqual(res.folder_id, 123)

    def test_response_folder_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FolderDeleteResponse()

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_folder_id_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FolderDeleteResponse(folder_id="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_folder_id_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FolderDeleteResponse(folder_id="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder_id",))
        self.assertEqual(e.get("type"), "int_parsing")
