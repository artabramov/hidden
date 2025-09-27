import unittest
from pydantic import ValidationError
from app.schemas.token_retrieve import (
    TokenRetrieveRequest, TokenRetrieveResponse)


class TokenRetrieveSchemaTest(unittest.TestCase):

    def test_request_correct(self):
        res = TokenRetrieveRequest(
            username="dummy",
            totp="123123",
            exp=300,
        )
        self.assertEqual(res.username, "dummy")
        self.assertEqual(res.totp, "123123")
        self.assertEqual(res.exp, 300)

    def test_request_username_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                totp="123123",
                exp=300,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_username_none(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                username=None,
                totp="123123",
                exp=300,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_totp_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                username="dummy",
                exp=300,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("totp",))
        self.assertEqual(e.get("type"), "missing")

    def test_request_totp_none(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                username="dummy",
                totp=None,
                exp=300,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("totp",))
        self.assertEqual(e.get("type"), "string_type")

    def test_request_totp_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                username="dummy",
                totp="12312",
                exp=300,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("totp",))
        self.assertEqual(e.get("type"), "string_too_short")

    def test_request_totp_too_long(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                username="dummy",
                totp="1231231",
                exp=300,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("totp",))
        self.assertEqual(e.get("type"), "string_too_long")

    def test_request_exp_missing(self):
        res = TokenRetrieveRequest(
            username="dummy",
            totp="123123",
        )
        self.assertEqual(res.username, "dummy")
        self.assertEqual(res.totp, "123123")
        self.assertEqual(res.exp, None)

    def test_request_exp_none(self):
        res = TokenRetrieveRequest(
            username="dummy",
            totp="123123",
            exp=None,
        )
        self.assertEqual(res.username, "dummy")
        self.assertEqual(res.totp, "123123")
        self.assertEqual(res.exp, None)

    def test_request_exp_integer_zero(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                username="dummy",
                totp="123123",
                exp=0,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("exp",))
        self.assertEqual(e.get("type"), "greater_than_equal")

    def test_request_exp_integer_coercion(self):
        res = TokenRetrieveRequest(
            username="dummy",
            totp="123123",
            exp="300",
        )
        self.assertEqual(res.username, "dummy")
        self.assertEqual(res.totp, "123123")
        self.assertEqual(res.exp, 300)

    def test_request_exp_string(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveRequest(
                username="dummy",
                totp="123123",
                exp="not-int",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("exp",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_correct(self):
        res = TokenRetrieveResponse(
            user_id=42, user_token="eyJhbGciOiJIUzI1")

        self.assertEqual(res.user_id, 42)
        self.assertEqual(res.user_token, "eyJhbGciOiJIUzI1")

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveResponse(
                user_token="eyJhbGciOiJIUzI1")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveResponse(
                user_id=None, user_token="eyJhbGciOiJIUzI1")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveResponse(
                user_id="not-int", user_token="eyJhbGciOiJIUzI1")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_coercion(self):
        res = TokenRetrieveResponse(
            user_id="42", user_token="eyJhbGciOiJIUzI1")

        self.assertEqual(res.user_id, 42)
        self.assertEqual(res.user_token, "eyJhbGciOiJIUzI1")

    def test_response_user_token_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveResponse(
                user_id=42)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_token",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_token_none(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveResponse(
                user_id=42, user_token=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_token",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_user_token_integer(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenRetrieveResponse(
                user_id=42, user_token=12)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_token",))
        self.assertEqual(e.get("type"), "string_type")
