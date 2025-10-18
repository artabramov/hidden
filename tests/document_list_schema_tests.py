import unittest
from pydantic import ValidationError
from app.schemas.file_list import (
    FileListRequest, FileListResponse)
from app.schemas.file_select import FileSelectResponse


class FileListSchemaTest(unittest.TestCase):

    def test_request_defaults(self):
        res = FileListRequest()
        self.assertIsNone(res.user_id__eq)
        self.assertIsNone(res.folder_id__eq)
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
        res = FileListRequest(
            user_id__eq=42,
            folder_id__eq=37,
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
        self.assertEqual(res.folder_id__eq, 37)
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
        res = FileListRequest(user_id__eq=None)
        self.assertIsNone(res.user_id__eq)

    def test_request_user_id_eq_integer_zero(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(user_id__eq=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_user_id_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(user_id__eq=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_user_id_eq_integer_positive(self):
        res = FileListRequest(user_id__eq=42)
        self.assertEqual(res.user_id__eq, 42)

    def test_request_user_id_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(user_id__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_user_id_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(user_id__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_user_id_eq_string_coercion(self):
        res = FileListRequest(user_id__eq="42")
        self.assertEqual(res.user_id__eq, 42)

    def test_request_user_id_eq_string_strip(self):
        res = FileListRequest(user_id__eq=" 42 ")
        self.assertEqual(res.user_id__eq, 42)

    def test_request_folder_id_eq_none(self):
        res = FileListRequest(folder_id__eq=None)
        self.assertIsNone(res.folder_id__eq)

    def test_request_folder_id_eq_integer_zero(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(folder_id__eq=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_folder_id_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(folder_id__eq=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_folder_id_eq_integer_positive(self):
        res = FileListRequest(folder_id__eq=42)
        self.assertEqual(res.folder_id__eq, 42)

    def test_request_folder_id_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(folder_id__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_folder_id_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(folder_id__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("folder_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_folder_id_eq_string_coercion(self):
        res = FileListRequest(folder_id__eq="42")
        self.assertEqual(res.folder_id__eq, 42)

    def test_request_folder_id_eq_string_strip(self):
        res = FileListRequest(folder_id__eq=" 42 ")
        self.assertEqual(res.folder_id__eq, 42)

    def test_request_created_date_ge_none(self):
        res = FileListRequest(created_date__ge=None)
        self.assertIsNone(res.created_date__ge)

    def test_request_created_date_ge_integer_zero(self):
        res = FileListRequest(created_date__ge=0)
        self.assertEqual(res.created_date__ge, 0)

    def test_request_created_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(created_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_ge_integer_positive(self):
        res = FileListRequest(created_date__ge=42)
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(created_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(created_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_coercion(self):
        res = FileListRequest(created_date__ge="42")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_strip(self):
        res = FileListRequest(created_date__ge=" 42 ")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_le_none(self):
        res = FileListRequest(created_date__le=None)
        self.assertIsNone(res.created_date__le)

    def test_request_created_date_le_integer_zero(self):
        res = FileListRequest(created_date__le=0)
        self.assertEqual(res.created_date__le, 0)

    def test_request_created_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(created_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_le_integer_positive(self):
        res = FileListRequest(created_date__le=42)
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(created_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(created_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_coercion(self):
        res = FileListRequest(created_date__le="42")
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_strip(self):
        res = FileListRequest(created_date__le=" 42 ")
        self.assertEqual(res.created_date__le, 42)

    def test_request_updated_date_ge_none(self):
        res = FileListRequest(updated_date__ge=None)
        self.assertIsNone(res.updated_date__ge)

    def test_request_updated_date_ge_integer_zero(self):
        res = FileListRequest(updated_date__ge=0)
        self.assertEqual(res.updated_date__ge, 0)

    def test_request_updated_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(updated_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_updated_date_ge_integer_positive(self):
        res = FileListRequest(updated_date__ge=42)
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(updated_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(updated_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_ge_string_coercion(self):
        res = FileListRequest(updated_date__ge="42")
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_ge_string_strip(self):
        res = FileListRequest(updated_date__ge=" 42 ")
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_le_none(self):
        res = FileListRequest(updated_date__le=None)
        self.assertIsNone(res.updated_date__le)

    def test_request_updated_date_le_integer_zero(self):
        res = FileListRequest(updated_date__le=0)
        self.assertEqual(res.updated_date__le, 0)

    def test_request_updated_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(updated_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_updated_date_le_integer_positive(self):
        res = FileListRequest(updated_date__le=42)
        self.assertEqual(res.updated_date__le, 42)

    def test_request_updated_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(updated_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(updated_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_le_string_coercion(self):
        res = FileListRequest(updated_date__le="42")
        self.assertEqual(res.updated_date__le, 42)

    def test_request_updated_date_le_string_strip(self):
        res = FileListRequest(updated_date__le=" 42 ")
        self.assertEqual(res.updated_date__le, 42)

    def test_request_flagged_eq_none(self):
        res = FileListRequest(flagged__eq=None)
        self.assertIsNone(res.flagged__eq)

    def test_request_flagged_eq_bool_false(self):
        res = FileListRequest(flagged__eq=False)
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_bool_true(self):
        res = FileListRequest(flagged__eq=True)
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_integer_0(self):
        res = FileListRequest(flagged__eq=0)
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_integer_1(self):
        res = FileListRequest(flagged__eq=1)
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_integer_2(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(flagged__eq=2)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(flagged__eq=-1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(flagged__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(flagged__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_flagged_eq_string_false(self):
        res = FileListRequest(flagged__eq="false")
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_string_true(self):
        res = FileListRequest(flagged__eq="true")
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_string_0(self):
        res = FileListRequest(flagged__eq="0")
        self.assertFalse(res.flagged__eq)

    def test_request_flagged_eq_string_1(self):
        res = FileListRequest(flagged__eq="1")
        self.assertTrue(res.flagged__eq)

    def test_request_flagged_eq_strip(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(flagged__eq=" 1 ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("flagged__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_filename_ilike_none(self):
        res = FileListRequest(filename__ilike=None)
        self.assertIsNone(res.filename__ilike)

    def test_request_filename_ilike_string_empty(self):
        res = FileListRequest(filename__ilike="")
        self.assertEqual(res.filename__ilike, "")

    def test_request_filename_ilike_string_dummy(self):
        res = FileListRequest(filename__ilike="dummy")
        self.assertEqual(res.filename__ilike, "dummy")

    def test_request_filename_ilike_string_strip(self):
        res = FileListRequest(filename__ilike=" dummy ")
        self.assertEqual(res.filename__ilike, "dummy")

    def test_request_filesize_ge_none(self):
        res = FileListRequest(filesize__ge=None)
        self.assertIsNone(res.filesize__ge)

    def test_request_filesize_ge_integer_zero(self):
        res = FileListRequest(filesize__ge=0)
        self.assertEqual(res.filesize__ge, 0)

    def test_request_filesize_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(filesize__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_filesize_ge_integer_positive(self):
        res = FileListRequest(filesize__ge=42)
        self.assertEqual(res.filesize__ge, 42)

    def test_request_filesize_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(filesize__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(filesize__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_ge_string_coercion(self):
        res = FileListRequest(filesize__ge="42")
        self.assertEqual(res.filesize__ge, 42)

    def test_request_filesize_ge_string_strip(self):
        res = FileListRequest(filesize__ge=" 42 ")
        self.assertEqual(res.filesize__ge, 42)

    def test_request_filesize_le_none(self):
        res = FileListRequest(filesize__le=None)
        self.assertIsNone(res.filesize__le)

    def test_request_filesize_le_integer_zero(self):
        res = FileListRequest(filesize__le=0)
        self.assertEqual(res.filesize__le, 0)

    def test_request_filesize_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(filesize__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_filesize_le_integer_positive(self):
        res = FileListRequest(filesize__le=42)
        self.assertEqual(res.filesize__le, 42)

    def test_request_filesize_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(filesize__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(filesize__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("filesize__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_filesize_le_string_coercion(self):
        res = FileListRequest(filesize__le="42")
        self.assertEqual(res.filesize__le, 42)

    def test_request_filesize_le_string_strip(self):
        res = FileListRequest(filesize__le=" 42 ")
        self.assertEqual(res.filesize__le, 42)

    def test_request_mimetype_ilike_none(self):
        res = FileListRequest(mimetype__ilike=None)
        self.assertIsNone(res.mimetype__ilike)

    def test_request_mimetype_ilike_string_empty(self):
        res = FileListRequest(mimetype__ilike="")
        self.assertEqual(res.mimetype__ilike, "")

    def test_request_mimetype_ilike_string_dummy(self):
        res = FileListRequest(mimetype__ilike="dummy")
        self.assertEqual(res.mimetype__ilike, "dummy")

    def test_request_mimetype_ilike_string_strip(self):
        res = FileListRequest(mimetype__ilike=" dummy ")
        self.assertEqual(res.mimetype__ilike, "dummy")

    def test_request_offset_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(offset=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_offset_ge_integer_zero(self):
        res = FileListRequest(offset=0)
        self.assertEqual(res.offset, 0)

    def test_request_offset_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(offset=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_offset_integer_positive(self):
        res = FileListRequest(offset=42)
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(offset="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(offset="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_coercion(self):
        res = FileListRequest(offset="42")
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_strip(self):
        res = FileListRequest(offset=" 42 ")
        self.assertEqual(res.offset, 42)

    def test_request_limit_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(limit=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_limit_ge_integer_0(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(limit=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_integer_1(self):
        res = FileListRequest(limit=1)
        self.assertEqual(res.limit, 1)

    def test_request_limit_integer_500(self):
        res = FileListRequest(limit=500)
        self.assertEqual(res.limit, 500)

    def test_request_limit_integer_501(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(limit=501)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "less_than_equal")

    def test_request_limit_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(limit=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(limit="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(limit="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_coercion(self):
        res = FileListRequest(limit="42")
        self.assertEqual(res.limit, 42)

    def test_request_limit_string_strip(self):
        res = FileListRequest(limit=" 42 ")
        self.assertEqual(res.limit, 42)

    def test_request_order_by_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order_by=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_literal(self):
        values = [
            "id", "created_date", "updated_date", "user_id",
            "folder_id", "flagged", "filename", "filesize",
            "mimetype"]

        for value in values:
            res = FileListRequest(order_by=value)
            self.assertEqual(res.order_by, value)

    def test_request_order_by_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order_by=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order_by="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order_by="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_literal(self):
        values = ["asc", "desc", "rand"]

        for value in values:
            res = FileListRequest(order=value)
            self.assertEqual(res.order, value)

    def test_request_order_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListRequest(order="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_response_correct(self):
        file_response = FileSelectResponse.model_construct(id=123)
        res = FileListResponse(
            files=[file_response], files_count=1)
        self.assertEqual(res.files, [file_response])
        self.assertEqual(res.files_count, 1)

    def test_response_files_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListResponse(files_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("files",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_files_none(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListResponse(files=None, files_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("files",))
        self.assertEqual(e.get("type"), "list_type")

    def test_response_files_list_invalid(self):
        with self.assertRaises(ValidationError) as ctx:
            FileListResponse(files=["dummy"], files_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("files", 0))
        self.assertEqual(e.get("type"), "model_type")

    def test_response_files_count_missing(self):
        file_response = FileSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            FileListResponse(files=[file_response])

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("files_count",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_files_count_none(self):
        file_response = FileSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            FileListResponse(
                files=[file_response], files_count=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("files_count",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_files_count_string(self):
        file_response = FileSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            FileListResponse(
                files=[file_response], files_count="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("files_count",))
        self.assertEqual(e.get("type"), "int_parsing")
