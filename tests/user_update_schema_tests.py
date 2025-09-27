import unittest
from pydantic import ValidationError
from app.schemas.user_update import UserUpdateRequest, UserUpdateResponse


class UserUpdateSchemaTest(unittest.TestCase):

    def test_request_correct(self):
        res = UserUpdateRequest(
            first_name="John",
            last_name="Doe",
            summary="Hello"
        )
        self.assertEqual(res.first_name, "John")
        self.assertEqual(res.last_name, "Doe")
        self.assertEqual(res.summary, "Hello")

    def test_request_extra_forbidden(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                first_name="John",
                last_name="Doe",
                summary="Hello",
                foo="bar"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("foo",))
        self.assertEqual(e.get("type"), "extra_forbidden")

    def test_request_first_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                last_name="Doe",
                summary="Hello"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_first_name_string_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                first_name="",
                last_name="Doe",
                summary="Hello"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_first_name_string_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                first_name="x" * 41,
                last_name="Doe",
                summary="Hello"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_first_name_string_shortest(self):
        res = UserUpdateRequest(
            first_name="x",
            last_name="Doe",
            summary="Hello"
        )
        self.assertEqual(res.first_name, "x")

    def test_request_first_name_string_longest(self):
        res = UserUpdateRequest(
            first_name="x" * 40,
            last_name="Doe",
            summary="Hello"
        )
        self.assertEqual(res.first_name, "x" * 40)

    def test_request_last_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                first_name="John",
                summary="Hello"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_last_name_string_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                first_name="John",
                last_name="",
                summary="Hello"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_last_name_string_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                first_name="John",
                last_name="x" * 41,
                summary="Hello"
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_last_name_string_shortest(self):
        res = UserUpdateRequest(
            first_name="John",
            last_name="x",
            summary="Hello"
        )
        self.assertEqual(res.last_name, "x")

    def test_request_last_name_string_longest(self):
        res = UserUpdateRequest(
            first_name="John",
            last_name="x" * 40,
            summary="Hello"
        )
        self.assertEqual(res.last_name, "x" * 40)

    def test_request_summary_none(self):
        res = UserUpdateRequest(
            first_name="John",
            last_name="Doe",
            summary=None
        )
        self.assertIsNone(res.summary)

    def test_request_summary_string_empty(self):
        res = UserUpdateRequest(
            first_name="John",
            last_name="Doe",
            summary=""
        )
        self.assertIsNone(res.summary)

    def test_request_summary_string_longest(self):
        res = UserUpdateRequest(
            first_name="John",
            last_name="Doe",
            summary="X" * 4096
        )
        self.assertEqual(res.summary, "X" * 4096)

    def test_request_summary_string_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateRequest(
                first_name="John",
                last_name="Doe",
                summary="X" * 4097
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_summary_string_stripped(self):
        res = UserUpdateRequest(
            first_name="John",
            last_name="Doe",
            summary=" X "
        )
        self.assertEqual(res.summary, "X")

    def test_response_correct(self):
        res = UserUpdateResponse(user_id=123)
        self.assertEqual(res.user_id, 123)

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateResponse()

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateResponse(user_id=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            UserUpdateResponse(user_id="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_coercion(self):
        res = UserUpdateResponse(user_id="123")
        self.assertEqual(res.user_id, 123)
