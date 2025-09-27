import unittest
from pydantic import ValidationError
from app.schemas.token_invalidate import TokenInvalidateResponse


class TokenInvalidateSchemaTest(unittest.TestCase):

    def test_response_correct(self):
        res = TokenInvalidateResponse(user_id=123)
        self.assertEqual(res.user_id, 123)

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenInvalidateResponse()

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenInvalidateResponse(user_id=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            TokenInvalidateResponse(user_id="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_coercion(self):
        res = TokenInvalidateResponse(user_id="123")
        self.assertEqual(res.user_id, 123)
