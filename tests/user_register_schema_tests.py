import unittest
from pydantic import ValidationError
from app.schemas.user_register import UserRegisterRequest, UserRegisterResponse


class UserRegisterSchemaTest(unittest.TestCase):

    def test_request_successful(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="John",
            last_name="Doe",
            summary="Hello",
        )
        self.assertEqual(res.username, "johndoe")
        self.assertEqual(res.first_name, "John")
        self.assertEqual(res.last_name, "Doe")
        self.assertEqual(res.password, "AaBb1!")
        self.assertEqual(res.summary, "Hello")

    def test_request_extra_forbidden(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                first_name="John",
                last_name="Doe",
                summary="Hello",
                foo="bar",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("foo",))
        self.assertEqual(e.get("type"), "extra_forbidden")

    def test_request_username_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                password="AaBb1!",
                first_name="John",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_username_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="",
                password="AaBb1!",
                first_name="John",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_username_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="x",
                password="AaBb1!",
                first_name="John",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_username_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="x" * 41,
                password="AaBb1!",
                first_name="John",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_username_shortest(self):
        res = UserRegisterRequest(
            username="x" * 2,
            password="AaBb1!",
            first_name="John",
            last_name="Doe",
            summary="Hello",
        )
        self.assertEqual(res.username, "x" * 2)

    def test_request_username_longest(self):
        res = UserRegisterRequest(
            username="x" * 40,
            password="AaBb1!",
            first_name="John",
            last_name="Doe",
            summary="Hello",
        )
        self.assertEqual(res.username, "x" * 40)

    def test_request_password_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_password_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="",
                first_name="John",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password",))
        self.assertEqual(e.get("type"), "too_short")

    def test_request_password_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="Aab1!",
                first_name="John",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("password",))
        self.assertEqual(e.get("type"), "too_short")

    def test_request_first_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_first_name_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                first_name="",
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_first_name_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                first_name="x" * 41,
                last_name="Doe",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_first_name_minimal_length(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="x",
            last_name="Doe",
            summary="Hello",
        )
        self.assertEqual(res.first_name, "x")

    def test_request_first_name_maximum_length(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="x" * 40,
            last_name="Doe",
            summary="Hello",
        )
        self.assertEqual(res.first_name, "x" * 40)

    def test_request_last_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                first_name="John",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_last_name_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                first_name="John",
                last_name="",
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_last_name_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                first_name="John",
                last_name="x" * 41,
                summary="Hello",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_last_name_minimal_length(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="John",
            last_name="x",
            summary="Hello",
        )
        self.assertEqual(res.last_name, "x")

    def test_request_last_name_maximum_length(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="John",
            last_name="x" * 40,
            summary="Hello",
        )
        self.assertEqual(res.last_name, "x" * 40)

    def test_request_summary_missing(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="John",
            last_name="Doe",
        )
        self.assertEqual(res.summary, None)

    def test_request_summary_empty(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="John",
            last_name="Doe",
        )
        self.assertEqual(res.summary, None)

    def test_request_summary_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterRequest(
                username="johndoe",
                password="AaBb1!",
                first_name="John",
                last_name="Doe",
                summary="x" * 4097,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_summary_longest(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="John",
            last_name="Doe",
            summary="x" * 4096,
        )
        self.assertEqual(res.summary, "x" * 4096)

    def test_request_summary_striped(self):
        res = UserRegisterRequest(
            username="johndoe",
            password="AaBb1!",
            first_name="John",
            last_name="Doe",
            summary=" x ",
        )
        self.assertEqual(res.summary, "x")

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterResponse(mfa_secret="ApmD8Jy3")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        self.assertEqual(errs[0].get("loc"), ("user_id",))
        self.assertEqual(errs[0].get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterResponse(user_id=None, mfa_secret="ApmD8Jy3")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterResponse(user_id="not-int", mfa_secret="ApmD8Jy3")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_coercion(self):
        res = UserRegisterResponse(user_id="123", mfa_secret="ApmD8Jy3")
        self.assertEqual(res.user_id, 123)

    def test_response_mfa_secret_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterResponse(user_id=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        self.assertEqual(errs[0].get("loc"), ("mfa_secret",))
        self.assertEqual(errs[0].get("type"), "missing")

    def test_response_mfa_secret_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegisterResponse(user_id=42, mfa_secret=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        self.assertEqual(errs[0].get("loc"), ("mfa_secret",))
        self.assertEqual(errs[0].get("type"), "string_type")
