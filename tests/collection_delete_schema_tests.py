import unittest
from pydantic import ValidationError
from app.schemas.collection_delete import CollectionDeleteResponse


class CollectionDeleteSchemaTest(unittest.TestCase):

    def test_response_correct(self):
        res = CollectionDeleteResponse(collection_id="123")
        self.assertEqual(res.collection_id, 123)

    def test_response_collection_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionDeleteResponse()

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_collection_id_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionDeleteResponse(collection_id="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_collection_id_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionDeleteResponse(collection_id="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "int_parsing")
