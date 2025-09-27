import unittest
from pydantic import ValidationError
from app.schemas.collection_list import (
    CollectionListRequest, CollectionListResponse)
from app.schemas.collection_select import CollectionSelectResponse


class CollectionListSchemaTest(unittest.TestCase):

    def test_request_defaults(self):
        res = CollectionListRequest()
        self.assertIsNone(res.user_id__eq)
        self.assertIsNone(res.created_date__ge)
        self.assertIsNone(res.created_date__le)
        self.assertIsNone(res.updated_date__ge)
        self.assertIsNone(res.updated_date__le)
        self.assertIsNone(res.readonly__eq)
        self.assertIsNone(res.name__ilike)
        self.assertEqual(res.offset, 0)
        self.assertEqual(res.limit, 50)
        self.assertEqual(res.order_by, "id")
        self.assertEqual(res.order, "desc")

    def test_request_correct(self):
        res = CollectionListRequest(
            user_id__eq=42,
            created_date__ge=0,
            created_date__le=99,
            updated_date__ge=10,
            updated_date__le=89,
            readonly__eq=True,
            name__ilike="docs",
            offset=10,
            limit=100,
            order_by="name",
            order="asc",
        )
        self.assertEqual(res.user_id__eq, 42)
        self.assertEqual(res.created_date__ge, 0)
        self.assertEqual(res.created_date__le, 99)
        self.assertEqual(res.updated_date__ge, 10)
        self.assertEqual(res.updated_date__le, 89)
        self.assertTrue(res.readonly__eq)
        self.assertEqual(res.name__ilike, "docs")
        self.assertEqual(res.offset, 10)
        self.assertEqual(res.limit, 100)
        self.assertEqual(res.order_by, "name")
        self.assertEqual(res.order, "asc")

    def test_request_user_id_eq_none(self):
        res = CollectionListRequest(user_id__eq=None)
        self.assertIsNone(res.user_id__eq)

    def test_request_user_id_eq_string_0(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(user_id__eq="0")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_user_id_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(user_id__eq=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_user_id_eq_integer_positive(self):
        res = CollectionListRequest(user_id__eq=42)
        self.assertEqual(res.user_id__eq, 42)

    def test_request_user_id_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(user_id__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_user_id_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(user_id__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id__eq",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_user_id_eq_string_coercion(self):
        res = CollectionListRequest(user_id__eq="42")
        self.assertEqual(res.user_id__eq, 42)

    def test_request_user_id_eq_string_strip(self):
        res = CollectionListRequest(user_id__eq=" 42 ")
        self.assertEqual(res.user_id__eq, 42)

    def test_request_created_date_ge_none(self):
        res = CollectionListRequest(created_date__ge=None)
        self.assertIsNone(res.created_date__ge)

    def test_request_created_date_ge_integer_zero(self):
        res = CollectionListRequest(created_date__ge=0)
        self.assertEqual(res.created_date__ge, 0)

    def test_request_created_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(created_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_ge_integer_positive(self):
        res = CollectionListRequest(created_date__ge=42)
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(created_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(created_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_coercion(self):
        res = CollectionListRequest(created_date__ge="42")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_strip(self):
        res = CollectionListRequest(created_date__ge=" 42 ")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_le_none(self):
        res = CollectionListRequest(created_date__le=None)
        self.assertIsNone(res.created_date__le)

    def test_request_created_date_le_integer_zero(self):
        res = CollectionListRequest(created_date__le=0)
        self.assertEqual(res.created_date__le, 0)

    def test_request_created_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(created_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_le_integer_positive(self):
        res = CollectionListRequest(created_date__le=42)
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(created_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(created_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_coercion(self):
        res = CollectionListRequest(created_date__le="42")
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_strip(self):
        res = CollectionListRequest(created_date__le=" 42 ")
        self.assertEqual(res.created_date__le, 42)

    def test_request_updated_date_ge_none(self):
        res = CollectionListRequest(updated_date__ge=None)
        self.assertIsNone(res.updated_date__ge)

    def test_request_updated_date_ge_integer_zero(self):
        res = CollectionListRequest(updated_date__ge=0)
        self.assertEqual(res.updated_date__ge, 0)

    def test_request_updated_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(updated_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_updated_date_ge_integer_positive(self):
        res = CollectionListRequest(updated_date__ge=42)
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(updated_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(updated_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_ge_string_coercion(self):
        res = CollectionListRequest(updated_date__ge="42")
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_ge_string_strip(self):
        res = CollectionListRequest(updated_date__ge=" 42 ")
        self.assertEqual(res.updated_date__ge, 42)

    def test_request_updated_date_le_none(self):
        res = CollectionListRequest(updated_date__le=None)
        self.assertIsNone(res.updated_date__le)

    def test_request_updated_date_le_integer_zero(self):
        res = CollectionListRequest(updated_date__le=0)
        self.assertEqual(res.updated_date__le, 0)

    def test_request_updated_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(updated_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_updated_date_le_integer_positive(self):
        res = CollectionListRequest(updated_date__le=42)
        self.assertEqual(res.updated_date__le, 42)

    def test_request_updated_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(updated_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(updated_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_updated_date_le_string_coercion(self):
        res = CollectionListRequest(updated_date__le="42")
        self.assertEqual(res.updated_date__le, 42)

    def test_request_updated_date_le_string_strip(self):
        res = CollectionListRequest(updated_date__le=" 42 ")
        self.assertEqual(res.updated_date__le, 42)

    def test_request_readonly_eq_none(self):
        res = CollectionListRequest(readonly__eq=None)
        self.assertIsNone(res.readonly__eq)

    def test_request_readonly_eq_bool_false(self):
        res = CollectionListRequest(readonly__eq=False)
        self.assertFalse(res.readonly__eq)

    def test_request_readonly_eq_bool_true(self):
        res = CollectionListRequest(readonly__eq=True)
        self.assertTrue(res.readonly__eq)

    def test_request_readonly_eq_integer_0(self):
        res = CollectionListRequest(readonly__eq=0)
        self.assertFalse(res.readonly__eq)

    def test_request_readonly_eq_integer_1(self):
        res = CollectionListRequest(readonly__eq=1)
        self.assertTrue(res.readonly__eq)

    def test_request_readonly_eq_integer_2(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(readonly__eq=2)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_readonly_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(readonly__eq=-1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_readonly_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(readonly__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_readonly_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(readonly__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_readonly_eq_string_false(self):
        res = CollectionListRequest(readonly__eq="false")
        self.assertFalse(res.readonly__eq)

    def test_request_readonly_eq_string_true(self):
        res = CollectionListRequest(readonly__eq="true")
        self.assertTrue(res.readonly__eq)

    def test_request_readonly_eq_string_0(self):
        res = CollectionListRequest(readonly__eq="0")
        self.assertFalse(res.readonly__eq)

    def test_request_readonly_eq_string_1(self):
        res = CollectionListRequest(readonly__eq="1")
        self.assertTrue(res.readonly__eq)

    def test_request_readonly_eq_strip(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(readonly__eq=" 1 ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_name_ilike_none(self):
        res = CollectionListRequest(name__ilike=None)
        self.assertIsNone(res.name__ilike)

    def test_request_name_ilike_string_empty(self):
        res = CollectionListRequest(name__ilike="")
        self.assertEqual(res.name__ilike, "")

    def test_request_name_ilike_string_dummy(self):
        res = CollectionListRequest(name__ilike="dummy")
        self.assertEqual(res.name__ilike, "dummy")

    def test_request_name_ilike_string_strip(self):
        res = CollectionListRequest(name__ilike=" dummy ")
        self.assertEqual(res.name__ilike, "dummy")

    def test_request_offset_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(offset=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_offset_ge_integer_zero(self):
        res = CollectionListRequest(offset=0)
        self.assertEqual(res.offset, 0)

    def test_request_offset_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(offset=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_offset_integer_positive(self):
        res = CollectionListRequest(offset=42)
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(offset="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(offset="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_coercion(self):
        res = CollectionListRequest(offset="42")
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_strip(self):
        res = CollectionListRequest(offset=" 42 ")
        self.assertEqual(res.offset, 42)

    def test_request_limit_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(limit=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_limit_ge_integer_0(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(limit=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_integer_1(self):
        res = CollectionListRequest(limit=1)
        self.assertEqual(res.limit, 1)

    def test_request_limit_integer_500(self):
        res = CollectionListRequest(limit=500)
        self.assertEqual(res.limit, 500)

    def test_request_limit_integer_501(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(limit=501)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "less_than_equal")

    def test_request_limit_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(limit=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(limit="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(limit="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_coercion(self):
        res = CollectionListRequest(limit="42")
        self.assertEqual(res.limit, 42)

    def test_request_limit_string_strip(self):
        res = CollectionListRequest(limit=" 42 ")
        self.assertEqual(res.limit, 42)

    def test_request_order_by_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order_by=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_literal(self):
        values = [
            "id", "created_date", "updated_date", "user_id",
            "readonly", "name"]

        for value in values:
            res = CollectionListRequest(order_by=value)
            self.assertEqual(res.order_by, value)

    def test_request_order_by_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order_by=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order_by="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order_by="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_literal(self):
        values = ["asc", "desc", "rand"]

        for value in values:
            res = CollectionListRequest(order=value)
            self.assertEqual(res.order, value)

    def test_request_order_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListRequest(order="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_response_correct(self):
        collection_response = CollectionSelectResponse.model_construct(id=123)
        res = CollectionListResponse(
            collections=[collection_response], collections_count=1)
        self.assertEqual(res.collections, [collection_response])
        self.assertEqual(res.collections_count, 1)

    def test_response_collections_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListResponse(collections_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collections",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_collections_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListResponse(collections=None, collections_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collections",))
        self.assertEqual(e.get("type"), "list_type")

    def test_response_collections_list_invalid(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionListResponse(collections=["dummy"], collections_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collections", 0))
        self.assertEqual(e.get("type"), "model_type")

    def test_response_collections_count_missing(self):
        collection_response = CollectionSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            CollectionListResponse(collections=[collection_response])

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collections_count",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_collections_count_none(self):
        collection_response = CollectionSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            CollectionListResponse(
                collections=[collection_response], collections_count=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collections_count",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_collections_count_string(self):
        collection_response = CollectionSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            CollectionListResponse(
                collections=[collection_response], collections_count="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("collections_count",))
        self.assertEqual(e.get("type"), "int_parsing")
