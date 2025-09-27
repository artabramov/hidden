import unittest
from pydantic import ValidationError
from app.schemas.user_login import UserLoginRequest, UserLoginResponse


class UserLoginSchemaTest(unittest.TestCase):

    def test_request_correct(self):
        res = UserLoginRequest(
            username="dummy",
            password="pass"
        )
        self.assertEqual(res.username, "dummy")
        self.assertEqual(res.password.get_secret_value(), "pass")

    def test_request_username_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginRequest(
                password="pass"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_username_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginRequest(
                username=None,
                password="pass"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_password_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginRequest(
                username="dummy"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_password_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginRequest(
                username="dummy",
                password=None
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_correct(self):
        res = UserLoginResponse(
            user_id=42, password_accepted=True)

        self.assertEqual(res.user_id, 42)
        self.assertEqual(res.password_accepted, True)

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginResponse(
                password_accepted=True)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginResponse(
                user_id=None, password_accepted=True)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginResponse(
                user_id="not-int", password_accepted=True)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_coercion(self):
        res = UserLoginResponse(
            user_id="42", password_accepted=True)

        self.assertEqual(res.user_id, 42)

    def test_response_password_accepted_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginResponse(
                user_id=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password_accepted",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_password_accepted_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginResponse(
                user_id=42, password_accepted=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password_accepted",))
        self.assertEqual(e.get("type"), "bool_type")

    def test_response_password_accepted_integer_0(self):
        res = UserLoginResponse(
            user_id="42", password_accepted=0)

        self.assertEqual(res.password_accepted, False)

    def test_response_password_accepted_integer_1(self):
        res = UserLoginResponse(
            user_id="42", password_accepted=1)

        self.assertEqual(res.password_accepted, True)

    def test_response_password_accepted_integer_2(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginResponse(
                user_id=42, password_accepted=2)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password_accepted",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_response_password_accepted_string_0(self):
        res = UserLoginResponse(
            user_id="42", password_accepted="0")

        self.assertEqual(res.password_accepted, False)

    def test_response_password_accepted_string_1(self):
        res = UserLoginResponse(
            user_id="42", password_accepted="1")

        self.assertEqual(res.password_accepted, True)

    def test_response_password_accepted_string_2(self):
        with self.assertRaises(ValidationError) as ctx:
            UserLoginResponse(
                user_id=42, password_accepted="2")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password_accepted",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_response_password_accepted_bool_true(self):
        res = UserLoginResponse(
            user_id="42", password_accepted=True)

        self.assertEqual(res.password_accepted, True)

    def test_response_password_accepted_bool_false(self):
        res = UserLoginResponse(
            user_id="42", password_accepted=False)

        self.assertEqual(res.password_accepted, False)
