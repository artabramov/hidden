import unittest
from pydantic import ValidationError
from app.schemas.document_list import (
    DocumentListRequest, DocumentListResponse)
from app.schemas.document_select import DocumentSelectResponse


class DocumentListSchemaTest(unittest.TestCase):

    def test_request_defaults(self):
        res = DocumentListRequest()
        self.assertIsNone(res.user_id__eq)
        self.assertIsNone(res.collection_id__eq)
        self.assertIsNone(res.created_date__ge)
        self.assertIsNone(res.created_date__le)
        self.assertIsNone(res.updated_date__ge)
        self.assertIsNone(res.updated_date__le)
        self.assertIsNone(res.flagged__eq)
        self.assertIsNone(res.filename__ilike)
        self.assertIsNone(res.filesize__ge)
        self.assertIsNone(res.filesize__le)
        self.assertIsNone(res.mimetype__ilike)
        self.assertEqual(res.offset, 0)
        self.assertEqual(res.limit, 50)
        self.assertEqual(res.order_by, "id")
        self.assertEqual(res.order, "desc")

    def test_request_correct(self):
        res = DocumentListRequest(
            user_id__eq=42,
            collection_id__eq=37,
            created_date__ge=0,
            created_date__le=99,
            updated_date__ge=10,
            updated_date__le=89,
            flagged__eq=True,
            filename__ilike="dummy",
            filesize__ge=100,
            filesize__le=200,
            mimetype__ilike="image/jpeg",
            offset=10,
            limit=100,
            order_by="filename",
            order="asc",
        )
        self.assertEqual(res.user_id__eq, 42)
        self.assertEqual(res.collection_id__eq, 37)
        self.assertEqual(res.created_date__ge, 0)
        self.assertEqual(res.created_date__le, 99)
        self.assertEqual(res.updated_date__ge, 10)
        self.assertEqual(res.updated_date__le, 89)
        self.assertTrue(res.flagged__eq)
        self.assertEqual(res.filename__ilike, "dummy")
        self.assertEqual(res.filesize__ge, 100)
        self.assertEqual(res.filesize__le, 200)
        self.assertEqual(res.mimetype__ilike, "image/jpeg")
        self.assertEqual(res.offset, 10)
        self.assertEqual(res.limit, 100)
        self.assertEqual(res.order_by, "filename")
        self.assertEqual(res.order, "asc")

    def test_request_user_id_eq_none(self):
        res = DocumentListRequest(user_id__eq=None)
        self.assertIsNone(res.user_id__eq)

    def test_request_user_id_eq_integer_zero(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(user_id__eq=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_user_id_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(user_id__eq=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_user_id_eq_integer_positive(self):
        res = DocumentListRequest(user_id__eq=42)
        self.assertEqual(res.user_id__eq, 42)

    def test_request_user_id_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(user_id__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_user_id_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(user_id__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_user_id_eq_string_coercion(self):
        res = DocumentListRequest(user_id__eq="42")
        self.assertEqual(res.user_id__eq, 42)

    def test_request_user_id_eq_string_strip(self):
        res = DocumentListRequest(user_id__eq=" 42 ")
        self.assertEqual(res.user_id__eq, 42)

    def test_request_collection_id_eq_none(self):
        res = DocumentListRequest(collection_id__eq=None)
        self.assertIsNone(res.collection_id__eq)

    def test_request_collection_id_eq_integer_zero(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(collection_id__eq=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_collection_id_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(collection_id__eq=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_collection_id_eq_integer_positive(self):
        res = DocumentListRequest(collection_id__eq=42)
        self.assertEqual(res.collection_id__eq, 42)

    def test_request_collection_id_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(collection_id__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_collection_id_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(collection_id__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collection_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_collection_id_eq_string_coercion(self):
        res = DocumentListRequest(collection_id__eq="42")
        self.assertEqual(res.collection_id__eq, 42)

    def test_request_collection_id_eq_string_strip(self):
        res = DocumentListRequest(collection_id__eq=" 42 ")
        self.assertEqual(res.collection_id__eq, 42)

    def test_request_created_date_ge_none(self):
        res = DocumentListRequest(created_date__ge=None)
        self.assertIsNone(res.created_date__ge)

    def test_request_created_date_ge_integer_zero(self):
        res = DocumentListRequest(created_date__ge=0)
        self.assertEqual(res.created_date__ge, 0)

    def test_request_created_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(created_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_ge_integer_positive(self):
        res = DocumentListRequest(created_date__ge=42)
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(created_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(created_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_coercion(self):
        res = DocumentListRequest(created_date__ge="42")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_strip(self):
        res = DocumentListRequest(created_date__ge=" 42 ")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_le_none(self):
        res = DocumentListRequest(created_date__le=None)
        self.assertIsNone(res.created_date__le)

    def test_request_created_date_le_integer_zero(self):
        res = DocumentListRequest(created_date__le=0)
        self.assertEqual(res.created_date__le, 0)

    def test_request_created_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(created_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_le_integer_positive(self):
        res = DocumentListRequest(created_date__le=42)
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(created_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(created_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_coercion(self):
        res = DocumentListRequest(created_date__le="42")
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_strip(self):
        res = DocumentListRequest(created_date__le=" 42 ")
        self.assertEqual(res.created_date__le, 42)

    def test_request_updated_date_ge_none(self):
        res = DocumentListRequest(updated_date__ge=None)
        self.assertIsNone(res.updated_date__ge)

    def test_request_updated_date_ge_integer_zero(self):
        res = DocumentListRequest(updated_date__ge=0)
        self.assertEqual(res.updated_date__ge, 0)

    def test_request_updated_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(updated_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_updated_date_ge_integer_positive(self):
        res = DocumentListRequest(updated_date__ge=42)
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(updated_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(updated_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_ge_string_coercion(self):
        res = DocumentListRequest(updated_date__ge="42")
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_ge_string_strip(self):
        res = DocumentListRequest(updated_date__ge=" 42 ")
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_le_none(self):
        res = DocumentListRequest(updated_date__le=None)
        self.assertIsNone(res.updated_date__le)

    def test_request_updated_date_le_integer_zero(self):
        res = DocumentListRequest(updated_date__le=0)
        self.assertEqual(res.updated_date__le, 0)

    def test_request_updated_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(updated_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_updated_date_le_integer_positive(self):
        res = DocumentListRequest(updated_date__le=42)
        self.assertEqual(res.updated_date__le, 42)

    def test_request_updated_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(updated_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(updated_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_le_string_coercion(self):
        res = DocumentListRequest(updated_date__le="42")
        self.assertEqual(res.updated_date__le, 42)

    def test_request_updated_date_le_string_strip(self):
        res = DocumentListRequest(updated_date__le=" 42 ")
        self.assertEqual(res.updated_date__le, 42)

    def test_request_flagged_eq_none(self):
        res = DocumentListRequest(flagged__eq=None)
        self.assertIsNone(res.flagged__eq)

    def test_request_flagged_eq_bool_false(self):
        res = DocumentListRequest(flagged__eq=False)
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_bool_true(self):
        res = DocumentListRequest(flagged__eq=True)
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_integer_0(self):
        res = DocumentListRequest(flagged__eq=0)
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_integer_1(self):
        res = DocumentListRequest(flagged__eq=1)
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_integer_2(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(flagged__eq=2)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(flagged__eq=-1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(flagged__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(flagged__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_string_false(self):
        res = DocumentListRequest(flagged__eq="false")
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_string_true(self):
        res = DocumentListRequest(flagged__eq="true")
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_string_0(self):
        res = DocumentListRequest(flagged__eq="0")
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_string_1(self):
        res = DocumentListRequest(flagged__eq="1")
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_strip(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(flagged__eq=" 1 ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_filename_ilike_none(self):
        res = DocumentListRequest(filename__ilike=None)
        self.assertIsNone(res.filename__ilike)

    def test_request_filename_ilike_string_empty(self):
        res = DocumentListRequest(filename__ilike="")
        self.assertEqual(res.filename__ilike, "")

    def test_request_filename_ilike_string_dummy(self):
        res = DocumentListRequest(filename__ilike="dummy")
        self.assertEqual(res.filename__ilike, "dummy")

    def test_request_filename_ilike_string_strip(self):
        res = DocumentListRequest(filename__ilike=" dummy ")
        self.assertEqual(res.filename__ilike, "dummy")

    def test_request_filesize_ge_none(self):
        res = DocumentListRequest(filesize__ge=None)
        self.assertIsNone(res.filesize__ge)

    def test_request_filesize_ge_integer_zero(self):
        res = DocumentListRequest(filesize__ge=0)
        self.assertEqual(res.filesize__ge, 0)

    def test_request_filesize_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(filesize__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_filesize_ge_integer_positive(self):
        res = DocumentListRequest(filesize__ge=42)
        self.assertEqual(res.filesize__ge, 42)

    def test_request_filesize_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(filesize__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(filesize__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_ge_string_coercion(self):
        res = DocumentListRequest(filesize__ge="42")
        self.assertEqual(res.filesize__ge, 42)

    def test_request_filesize_ge_string_strip(self):
        res = DocumentListRequest(filesize__ge=" 42 ")
        self.assertEqual(res.filesize__ge, 42)

    def test_request_filesize_le_none(self):
        res = DocumentListRequest(filesize__le=None)
        self.assertIsNone(res.filesize__le)

    def test_request_filesize_le_integer_zero(self):
        res = DocumentListRequest(filesize__le=0)
        self.assertEqual(res.filesize__le, 0)

    def test_request_filesize_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(filesize__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_filesize_le_integer_positive(self):
        res = DocumentListRequest(filesize__le=42)
        self.assertEqual(res.filesize__le, 42)

    def test_request_filesize_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(filesize__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(filesize__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_le_string_coercion(self):
        res = DocumentListRequest(filesize__le="42")
        self.assertEqual(res.filesize__le, 42)

    def test_request_filesize_le_string_strip(self):
        res = DocumentListRequest(filesize__le=" 42 ")
        self.assertEqual(res.filesize__le, 42)

    def test_request_mimetype_ilike_none(self):
        res = DocumentListRequest(mimetype__ilike=None)
        self.assertIsNone(res.mimetype__ilike)

    def test_request_mimetype_ilike_string_empty(self):
        res = DocumentListRequest(mimetype__ilike="")
        self.assertEqual(res.mimetype__ilike, "")

    def test_request_mimetype_ilike_string_dummy(self):
        res = DocumentListRequest(mimetype__ilike="dummy")
        self.assertEqual(res.mimetype__ilike, "dummy")

    def test_request_mimetype_ilike_string_strip(self):
        res = DocumentListRequest(mimetype__ilike=" dummy ")
        self.assertEqual(res.mimetype__ilike, "dummy")

    def test_request_offset_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(offset=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_offset_ge_integer_zero(self):
        res = DocumentListRequest(offset=0)
        self.assertEqual(res.offset, 0)

    def test_request_offset_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(offset=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_offset_integer_positive(self):
        res = DocumentListRequest(offset=42)
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(offset="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(offset="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_coercion(self):
        res = DocumentListRequest(offset="42")
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_strip(self):
        res = DocumentListRequest(offset=" 42 ")
        self.assertEqual(res.offset, 42)

    def test_request_limit_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(limit=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_limit_ge_integer_0(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(limit=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_integer_1(self):
        res = DocumentListRequest(limit=1)
        self.assertEqual(res.limit, 1)

    def test_request_limit_integer_500(self):
        res = DocumentListRequest(limit=500)
        self.assertEqual(res.limit, 500)

    def test_request_limit_integer_501(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(limit=501)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "less_than_equal")

    def test_request_limit_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(limit=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(limit="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(limit="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_coercion(self):
        res = DocumentListRequest(limit="42")
        self.assertEqual(res.limit, 42)

    def test_request_limit_string_strip(self):
        res = DocumentListRequest(limit=" 42 ")
        self.assertEqual(res.limit, 42)

    def test_request_order_by_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order_by=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_literal(self):
        values = [
            "id", "created_date", "updated_date", "user_id",
            "collection_id", "flagged", "filename", "filesize",
            "mimetype"]

        for value in values:
            res = DocumentListRequest(order_by=value)
            self.assertEqual(res.order_by, value)

    def test_request_order_by_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order_by=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order_by="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order_by="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_literal(self):
        values = ["asc", "desc", "rand"]

        for value in values:
            res = DocumentListRequest(order=value)
            self.assertEqual(res.order, value)

    def test_request_order_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListRequest(order="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_response_correct(self):
        document_response = DocumentSelectResponse.model_construct(id=123)
        res = DocumentListResponse(
            documents=[document_response], documents_count=1)
        self.assertEqual(res.documents, [document_response])
        self.assertEqual(res.documents_count, 1)

    def test_response_documents_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListResponse(documents_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("documents",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_documents_none(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListResponse(documents=None, documents_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("documents",))
        self.assertEqual(e.get("type"), "list_type")

    def test_response_documents_list_invalid(self):
        with self.assertRaises(ValidationError) as ctx:
            DocumentListResponse(documents=["dummy"], documents_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("documents", 0))
        self.assertEqual(e.get("type"), "model_type")

    def test_response_documents_count_missing(self):
        document_response = DocumentSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            DocumentListResponse(documents=[document_response])

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("documents_count",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_documents_count_none(self):
        document_response = DocumentSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            DocumentListResponse(
                documents=[document_response], documents_count=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("documents_count",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_documents_count_string(self):
        document_response = DocumentSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            DocumentListResponse(
                documents=[document_response], documents_count="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("documents_count",))
        self.assertEqual(e.get("type"), "int_parsing")
