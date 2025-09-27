import unittest
from pydantic import ValidationError
from app.schemas.user_list import UserListRequest, UserListResponse
from app.schemas.user_select import UserSelectResponse


class UserListSchemaTest(unittest.TestCase):

    def test_request_defaults(self):
        res = UserListRequest()
        self.assertIsNone(res.created_date__ge)
        self.assertIsNone(res.created_date__le)
        self.assertIsNone(res.last_login_date__ge)
        self.assertIsNone(res.last_login_date__le)
        self.assertIsNone(res.active__eq)
        self.assertIsNone(res.role__eq)
        self.assertIsNone(res.username__ilike)
        self.assertIsNone(res.first_name__ilike)
        self.assertIsNone(res.last_name__ilike)
        self.assertIsNone(res.full_name__ilike)
        self.assertEqual(res.offset, 0)
        self.assertEqual(res.limit, 50)
        self.assertEqual(res.order_by, "id")
        self.assertEqual(res.order, "desc")

    def test_request_correct(self):
        res = UserListRequest(
            created_date__ge=0,
            created_date__le=99,
            last_login_date__ge=10,
            last_login_date__le=89,
            active__eq=True,
            role__eq="reader",
            username__ilike="johndoe",
            first_name__ilike="john",
            last_name__ilike="doe",
            full_name__ilike="john doe",
            offset=10,
            limit=100,
            order_by="username",
            order="asc",
        )
        self.assertEqual(res.created_date__ge, 0)
        self.assertEqual(res.created_date__le, 99)
        self.assertEqual(res.last_login_date__ge, 10)
        self.assertEqual(res.last_login_date__le, 89)
        self.assertTrue(res.active__eq)
        self.assertEqual(res.role__eq, "reader")
        self.assertEqual(res.username__ilike, "johndoe")
        self.assertEqual(res.first_name__ilike, "john")
        self.assertEqual(res.last_name__ilike, "doe")
        self.assertEqual(res.full_name__ilike, "john doe")
        self.assertEqual(res.offset, 10)
        self.assertEqual(res.limit, 100)
        self.assertEqual(res.order_by, "username")
        self.assertEqual(res.order, "asc")

    def test_request_created_date_ge_none(self):
        res = UserListRequest(created_date__ge=None)
        self.assertIsNone(res.created_date__ge)

    def test_request_created_date_ge_integer_zero(self):
        res = UserListRequest(created_date__ge=0)
        self.assertEqual(res.created_date__ge, 0)

    def test_request_created_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(created_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_ge_integer_positive(self):
        res = UserListRequest(created_date__ge=42)
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(created_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(created_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_ge_string_coercion(self):
        res = UserListRequest(created_date__ge="42")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_ge_string_strip(self):
        res = UserListRequest(created_date__ge=" 42 ")
        self.assertEqual(res.created_date__ge, 42)

    def test_request_created_date_le_none(self):
        res = UserListRequest(created_date__le=None)
        self.assertIsNone(res.created_date__le)

    def test_request_created_date_le_integer_zero(self):
        res = UserListRequest(created_date__le=0)
        self.assertEqual(res.created_date__le, 0)

    def test_request_created_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(created_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_created_date_le_integer_positive(self):
        res = UserListRequest(created_date__le=42)
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(created_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(created_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("created_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_created_date_le_string_coercion(self):
        res = UserListRequest(created_date__le="42")
        self.assertEqual(res.created_date__le, 42)

    def test_request_created_date_le_string_strip(self):
        res = UserListRequest(created_date__le=" 42 ")
        self.assertEqual(res.created_date__le, 42)

    def test_request_last_login_date_ge_none(self):
        res = UserListRequest(last_login_date__ge=None)
        self.assertIsNone(res.last_login_date__ge)

    def test_request_last_login_date_ge_integer_zero(self):
        res = UserListRequest(last_login_date__ge=0)
        self.assertEqual(res.last_login_date__ge, 0)

    def test_request_last_login_date_ge_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(last_login_date__ge=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_login_date__ge",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_last_login_date_ge_integer_positive(self):
        res = UserListRequest(last_login_date__ge=42)
        self.assertEqual(res.last_login_date__ge, 42)

    def test_request_last_login_date_ge_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(last_login_date__ge="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_login_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_last_login_date_ge_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(last_login_date__ge="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_login_date__ge",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_last_login_date_ge_string_coercion(self):
        res = UserListRequest(last_login_date__ge="42")
        self.assertEqual(res.last_login_date__ge, 42)

    def test_request_last_login_date_ge_string_strip(self):
        res = UserListRequest(last_login_date__ge=" 42 ")
        self.assertEqual(res.last_login_date__ge, 42)

    def test_request_last_login_date_le_none(self):
        res = UserListRequest(last_login_date__le=None)
        self.assertIsNone(res.last_login_date__le)

    def test_request_last_login_date_le_integer_zero(self):
        res = UserListRequest(last_login_date__le=0)
        self.assertEqual(res.last_login_date__le, 0)

    def test_request_last_login_date_le_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(last_login_date__le=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_login_date__le",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_last_login_date_le_integer_positive(self):
        res = UserListRequest(last_login_date__le=42)
        self.assertEqual(res.last_login_date__le, 42)

    def test_request_last_login_date_le_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(last_login_date__le="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_login_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_last_login_date_le_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(last_login_date__le="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_login_date__le",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_last_login_date_le_string_coercion(self):
        res = UserListRequest(last_login_date__le="42")
        self.assertEqual(res.last_login_date__le, 42)

    def test_request_last_login_date_le_string_strip(self):
        res = UserListRequest(last_login_date__le=" 42 ")
        self.assertEqual(res.last_login_date__le, 42)

    def test_request_active_eq_none(self):
        res = UserListRequest(active__eq=None)
        self.assertIsNone(res.active__eq)

    def test_request_active_eq_bool_false(self):
        res = UserListRequest(active__eq=False)
        self.assertFalse(res.active__eq)

    def test_request_active_eq_bool_true(self):
        res = UserListRequest(active__eq=True)
        self.assertTrue(res.active__eq)

    def test_request_active_eq_integer_0(self):
        res = UserListRequest(active__eq=0)
        self.assertFalse(res.active__eq)

    def test_request_active_eq_integer_1(self):
        res = UserListRequest(active__eq=1)
        self.assertTrue(res.active__eq)

    def test_request_active_eq_integer_2(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(active__eq=2)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_active_eq_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(active__eq=-1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_active_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(active__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_active_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(active__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_active_eq_string_false(self):
        res = UserListRequest(active__eq="false")
        self.assertFalse(res.active__eq)

    def test_request_active_eq_string_true(self):
        res = UserListRequest(active__eq="true")
        self.assertTrue(res.active__eq)

    def test_request_active_eq_string_0(self):
        res = UserListRequest(active__eq="0")
        self.assertFalse(res.active__eq)

    def test_request_active_eq_string_1(self):
        res = UserListRequest(active__eq="1")
        self.assertTrue(res.active__eq)

    def test_request_active_eq_strip(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(active__eq=" 1 ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active__eq",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_role_eq_none(self):
        res = UserListRequest(role__eq=None)
        self.assertIsNone(res.role__eq)

    def test_request_role_eq_literal(self):
        roles = ["reader", "writer", "editor", "admin"]
        for role in roles:
            res = UserListRequest(role__eq=role)
            self.assertEqual(res.role__eq, role)

    def test_request_role_eq_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(role__eq="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role__eq",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_role_eq_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(role__eq="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role__eq",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_username_ilike_none(self):
        res = UserListRequest(username__ilike=None)
        self.assertIsNone(res.username__ilike)

    def test_request_username_ilike_string_empty(self):
        res = UserListRequest(username__ilike="")
        self.assertEqual(res.username__ilike, "")

    def test_request_username_ilike_string_dummy(self):
        res = UserListRequest(username__ilike="dummy")
        self.assertEqual(res.username__ilike, "dummy")

    def test_request_username_ilike_string_strip(self):
        res = UserListRequest(username__ilike=" dummy ")
        self.assertEqual(res.username__ilike, "dummy")

    def test_request_first_name_ilike_none(self):
        res = UserListRequest(first_name__ilike=None)
        self.assertIsNone(res.first_name__ilike)

    def test_request_first_name_ilike_string_empty(self):
        res = UserListRequest(first_name__ilike="")
        self.assertEqual(res.first_name__ilike, "")

    def test_request_first_name_ilike_string_dummy(self):
        res = UserListRequest(first_name__ilike="dummy")
        self.assertEqual(res.first_name__ilike, "dummy")

    def test_request_first_name_ilike_string_strip(self):
        res = UserListRequest(first_name__ilike=" dummy ")
        self.assertEqual(res.first_name__ilike, "dummy")

    def test_request_last_name_ilike_none(self):
        res = UserListRequest(last_name__ilike=None)
        self.assertIsNone(res.last_name__ilike)

    def test_request_last_name_ilike_string_empty(self):
        res = UserListRequest(last_name__ilike="")
        self.assertEqual(res.last_name__ilike, "")

    def test_request_last_name_ilike_string_dummy(self):
        res = UserListRequest(last_name__ilike="dummy")
        self.assertEqual(res.last_name__ilike, "dummy")

    def test_request_last_name_ilike_string_strip(self):
        res = UserListRequest(last_name__ilike=" dummy ")
        self.assertEqual(res.last_name__ilike, "dummy")

    def test_request_full_name_ilike_none(self):
        res = UserListRequest(full_name__ilike=None)
        self.assertIsNone(res.full_name__ilike)

    def test_request_full_name_ilike_string_empty(self):
        res = UserListRequest(full_name__ilike="")
        self.assertEqual(res.full_name__ilike, "")

    def test_request_full_name_ilike_string_dummy(self):
        res = UserListRequest(full_name__ilike="dummy")
        self.assertEqual(res.full_name__ilike, "dummy")

    def test_request_full_name_ilike_string_strip(self):
        res = UserListRequest(full_name__ilike=" dummy ")
        self.assertEqual(res.full_name__ilike, "dummy")

    def test_request_offset_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(offset=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_offset_ge_integer_zero(self):
        res = UserListRequest(offset=0)
        self.assertEqual(res.offset, 0)

    def test_request_offset_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(offset=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_offset_integer_positive(self):
        res = UserListRequest(offset=42)
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(offset="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(offset="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("offset",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_offset_string_coercion(self):
        res = UserListRequest(offset="42")
        self.assertEqual(res.offset, 42)

    def test_request_offset_string_strip(self):
        res = UserListRequest(offset=" 42 ")
        self.assertEqual(res.offset, 42)

    def test_request_limit_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(limit=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_type")

    def test_request_limit_ge_integer_0(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(limit=0)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_integer_1(self):
        res = UserListRequest(limit=1)
        self.assertEqual(res.limit, 1)

    def test_request_limit_integer_500(self):
        res = UserListRequest(limit=500)
        self.assertEqual(res.limit, 500)

    def test_request_limit_integer_501(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(limit=501)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "less_than_equal")

    def test_request_limit_integer_negative(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(limit=-42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_limit_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(limit="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(limit="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("limit",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_request_limit_string_coercion(self):
        res = UserListRequest(limit="42")
        self.assertEqual(res.limit, 42)

    def test_request_limit_string_strip(self):
        res = UserListRequest(limit=" 42 ")
        self.assertEqual(res.limit, 42)

    def test_request_order_by_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order_by=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_literal(self):
        values = [
            "id", "created_date", "last_login_date", "role", "active",
            "username", "first_name", "last_name", "full_name"]

        for value in values:
            res = UserListRequest(order_by=value)
            self.assertEqual(res.order_by, value)

    def test_request_order_by_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order_by=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order_by="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_by_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order_by="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order_by",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_literal(self):
        values = ["asc", "desc", "rand"]

        for value in values:
            res = UserListRequest(order=value)
            self.assertEqual(res.order, value)

    def test_request_order_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order=" id ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_order_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListRequest(order="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("order",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_response_correct(self):
        user_response = UserSelectResponse.model_construct(id=123)
        res = UserListResponse(
            users=[user_response], users_count=1)
        self.assertEqual(res.users, [user_response])
        self.assertEqual(res.users_count, 1)

    def test_response_users_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListResponse(users_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("users",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_users_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListResponse(users=None, users_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("users",))
        self.assertEqual(e.get("type"), "list_type")

    def test_response_users_list_invalid(self):
        with self.assertRaises(ValidationError) as ctx:
            UserListResponse(users=["dummy"], users_count=1)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("users", 0))
        self.assertEqual(e.get("type"), "model_type")

    def test_response_users_count_missing(self):
        user_response = UserSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            UserListResponse(users=[user_response])

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("users_count",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_users_count_none(self):
        user_response = UserSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            UserListResponse(
                users=[user_response], users_count=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("users_count",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_users_count_string(self):
        user_response = UserSelectResponse.model_construct(id=123)
        with self.assertRaises(ValidationError) as ctx:
            UserListResponse(
                users=[user_response], users_count="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("users_count",))
        self.assertEqual(e.get("type"), "int_parsing")
