import unittest
from pydantic import ValidationError
from app.schemas.userpic_delete import UserpicDeleteResponse


class UserDeleteSchemaTest(unittest.TestCase):

    def test_response_correct(self):
        res = UserpicDeleteResponse(user_id=123)
        self.assertEqual(res.user_id, 123)

    def test_response_user_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserpicDeleteResponse()

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserpicDeleteResponse(user_id=None)

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_user_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            UserpicDeleteResponse(user_id="not-int")

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user_id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_user_id_coercion(self):
        res = UserpicDeleteResponse(user_id="123")
        self.assertEqual(res.user_id, 123)
