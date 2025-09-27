import unittest
from pydantic import ValidationError
from app.schemas.user_role import UserRoleRequest, UserRoleResponse


class UserRoleSchemasTest(unittest.TestCase):

    def test_request_successful(self):
        res = UserRoleRequest(role="reader", active="true")
        self.assertEqual(res.role, "reader")
        self.assertEqual(res.active, True)

    def test_request_extra_forbidden(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="reader", active="true", foo="bar")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("foo",))
        self.assertEqual(e.get("type"), "extra_forbidden")

    def test_request_role_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(active="true")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_role_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="", active="true")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_role_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="dummy", active="true")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_role_literal(self):
        roles = ["reader", "writer", "editor", "admin"]
        for role in roles:
            res = UserRoleRequest(role=role, active="true")

        self.assertEqual(res.role, role)

    def test_request_role_string_not_stripped(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role=" reader ", active="true")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_request_active_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="reader")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_active_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="reader", active="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_active_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="reader", active="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_active_string_0(self):
        res = UserRoleRequest(role="reader", active="0")
        self.assertEqual(res.active, False)

    def test_request_active_string_1(self):
        res = UserRoleRequest(role="reader", active="1")
        self.assertEqual(res.active, True)

    def test_request_active_string_2(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="reader", active="2")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_request_active_string_true(self):
        res = UserRoleRequest(role="reader", active="true")
        self.assertEqual(res.active, True)

    def test_request_active_string_false(self):
        res = UserRoleRequest(role="reader", active="false")
        self.assertEqual(res.active, False)

    def test_request_active_string_not_stripped(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleRequest(role="reader", active=" true ")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_response_correct(self):
        res = UserRoleResponse(user_id=123)
        self.assertEqual(res.user_id, 123)

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleResponse()

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleResponse(user_id=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleResponse(user_id="")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRoleResponse(user_id="dummy")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_string_integer(self):
        res = UserRoleResponse(user_id="123")
        self.assertEqual(res.user_id, 123)
