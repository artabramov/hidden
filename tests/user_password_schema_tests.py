import unittest
from pydantic import ValidationError
from app.schemas.user_password import UserPasswordRequest, UserPasswordResponse


class UserPasswordSchemaTest(unittest.TestCase):

    def test_request_valid(self):
        res = UserPasswordRequest(
            current_password="  OldP@1  ",
            updated_password="NewP@1",
        )
        self.assertEqual(res.current_password, "OldP@1")
        self.assertEqual(res.updated_password, "NewP@1")

    def test_request_current_password_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                updated_password="NewP@1",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("current_password",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_current_password_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                current_password=None,
                updated_password="NewP@1",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("current_password",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_current_password_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                current_password="",
                updated_password="NewP@1",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("current_password",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_current_password_string_length_5(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                current_password="OldP@",
                updated_password="NewP@1",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("current_password",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_updated_password_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                current_password="OldP@1",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_password",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_updated_password_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                current_password="OldP@1",
                updated_password=None,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_password",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_updated_password_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                current_password="OldP@1",
                updated_password="",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_password",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_updated_password_string_length_5(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordRequest(
                current_password="OldP@1",
                updated_password="NewP@",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("updated_password",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_updated_password_complexity_enforced(self):
        passwords = ["AA1!AA", "aa1!aa", "Aa!aaa", "Aa1aaa", "Aa1! a"]
        for password in passwords:
            with self.assertRaises(ValidationError) as ctx:
                UserPasswordRequest(
                    current_password="OldP@1",
                    updated_password=password,
                )

            errs = ctx.exception.errors()
            self.assertEqual(len(errs), 1)

            e = errs[0]
            self.assertEqual(e.get("loc"), ("updated_password",))
            self.assertEqual(e.get("type"), "value_error")

    def test_response_valid(self):
        res = UserPasswordResponse(user_id=123)
        self.assertEqual(res.user_id, 123)

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordResponse()

            errs = ctx.exception.errors()
            self.assertEqual(len(errs), 1)

            e = errs[0]
            self.assertEqual(e.get("loc"), ("user_id",))
            self.assertEqual(e.get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordResponse(user_id=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            UserPasswordResponse(user_id="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_coercion_from_str(self):
        res = UserPasswordResponse(user_id="42")
        self.assertEqual(res.user_id, 42)
