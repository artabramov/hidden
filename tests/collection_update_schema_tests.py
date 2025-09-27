import unittest
from pydantic import ValidationError
from app.schemas.collection_update import (
    CollectionUpdateRequest, CollectionUpdateResponse)


class CollectionUpdateSchemaTest(unittest.TestCase):

    def test_request_correct(self):
        res = CollectionUpdateRequest(readonly=False, name="Dummy")
        self.assertEqual(res.name, "Dummy")
        self.assertFalse(res.readonly)
        self.assertIsNone(res.summary)

    def test_request_readonly_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(name="Dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_readonly_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(readonly=None, name="Dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly",))
        self.assertEqual(e.get("type"), "bool_type")

    def test_request_readonly_string(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(readonly="not-int", name="Dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_readonly_integer(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(readonly=123, name="Dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_readonly_coercion_integer_0(self):
        res = CollectionUpdateRequest(readonly=0, name="Dummy")
        self.assertEqual(res.readonly, False)

    def test_request_readonly_coercion_integer_1(self):
        res = CollectionUpdateRequest(readonly=1, name="Dummy")
        self.assertEqual(res.readonly, True)

    def test_request_readonly_coercion_string_0(self):
        res = CollectionUpdateRequest(readonly="0", name="Dummy")
        self.assertEqual(res.readonly, False)

    def test_request_readonly_coercion_string_1(self):
        res = CollectionUpdateRequest(readonly="1", name="Dummy")
        self.assertEqual(res.readonly, True)

    def test_request_readonly_coercion_string_false(self):
        res = CollectionUpdateRequest(readonly="false", name="Dummy")
        self.assertEqual(res.readonly, False)

    def test_request_readonly_coercion_string_true(self):
        res = CollectionUpdateRequest(readonly="true", name="Dummy")
        self.assertEqual(res.readonly, True)

    def test_request_readonly_false(self):
        res = CollectionUpdateRequest(readonly=False, name="Dummy")
        self.assertEqual(res.readonly, False)

    def test_request_readonly_true(self):
        res = CollectionUpdateRequest(readonly=True, name="Dummy")
        self.assertEqual(res.readonly, True)

    def test_request_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(readonly=False)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("name",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_name_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(readonly=False, name=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("name",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_name_string_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(readonly=False, name="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("name",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_name_string_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(readonly=False, name="X" * 256)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("name",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_name_string_shortest(self):
        res = CollectionUpdateRequest(readonly=False, name="X")
        self.assertEqual(res.name, "X")

    def test_request_name_string_longest(self):
        res = CollectionUpdateRequest(readonly=False, name="X" * 255)
        self.assertEqual(res.name, "X" * 255)

    def test_request_name_string_stripped(self):
        res = CollectionUpdateRequest(readonly=False, name=" X ")
        self.assertEqual(res.name, "X")

    def test_request_summary_none(self):
        res = CollectionUpdateRequest(
            readonly=False, name="Dummy", summary=None)
        self.assertIsNone(res.summary)

    def test_request_summary_string_empty(self):
        res = CollectionUpdateRequest(
            readonly=False, name="Dummy", summary="")
        self.assertIsNone(res.summary)

    def test_request_summary_string_longest(self):
        res = CollectionUpdateRequest(
            readonly=False, name="Dummy", summary="X" * 4096)
        self.assertEqual(res.summary, "X" * 4096)

    def test_request_summary_string_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(
                readonly=False, name="Dummy", summary="X" * 4097)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_summary_integer(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(
                readonly=False, name="Dummy", summary=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_summary_string_stripped(self):
        res = CollectionUpdateRequest(
            readonly=False, name="Dummy", summary=" X ")
        self.assertEqual(res.summary, "X")

    def test_request_extra_forbidden(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateRequest(
                readonly=False, name="Dummy", foo="bar")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("foo",))
        self.assertEqual(e.get("type"), "extra_forbidden")

    def test_response_correct(self):
        res = CollectionUpdateResponse(collection_id=123)
        self.assertEqual(res.collection_id, 123)

    def test_response_collection_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateResponse()

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_collection_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateResponse(collection_id=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_collection_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionUpdateResponse(collection_id="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_collection_id_coercion(self):
        res = CollectionUpdateResponse(collection_id="123")
        self.assertEqual(res.collection_id, 123)
