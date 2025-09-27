import unittest
from pydantic import ValidationError
from app.schemas.collection_select import (
    CollectionSelectResponse, UserSelectResponse)


class CollectionSelectSchemaTest(unittest.TestCase):

    def _user_stub(self):
        # Create a valid UserSelectResponse instance without binding it
        # to specific user schema fields (bypassing field validation).
        # This prevents from breaking when the user schema changes.
        return UserSelectResponse.model_construct(id=123)

    def test_response_correct(self):
        res = CollectionSelectResponse(
            id=42,
            created_date=100,
            updated_date=200,
            readonly=True,
            name="X",
            summary=None,
            user=self._user_stub(),
        )
        self.assertEqual(res.id, 42)
        self.assertEqual(res.user, self._user_stub())
        self.assertEqual(res.created_date, 100)
        self.assertEqual(res.updated_date, 200)
        self.assertEqual(res.readonly, True)
        self.assertEqual(res.name, "X")
        self.assertIsNone(res.summary)

    def test_response_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                created_date=100,
                updated_date=200,
                readonly=True,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=None,
                created_date=100,
                updated_date=200,
                readonly=True,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id="not-int",
                created_date=100,
                updated_date=200,
                readonly=True,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_id_coercion(self):
        res = CollectionSelectResponse(
            id="42",
            created_date=100,
            updated_date=200,
            readonly=True,
            name="X",
            summary=None,
            user=self._user_stub(),
        )
        self.assertEqual(res.id, 42)

    def test_response_timestamps_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                readonly=True,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "missing")

        self.assertEqual(errs[1].get("loc"), ("updated_date",))
        self.assertEqual(errs[1].get("type"), "missing")

    def test_response_timestamps_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=None,
                updated_date=None,
                readonly=True,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_type")

        self.assertEqual(errs[1].get("loc"), ("updated_date",))
        self.assertEqual(errs[1].get("type"), "int_type")

    def test_response_timestamps_string(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date="not-int",
                updated_date="not-int",
                readonly=True,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_parsing")

        self.assertEqual(errs[1].get("loc"), ("updated_date",))
        self.assertEqual(errs[1].get("type"), "int_parsing")

    def test_response_timestamps_coercion(self):
        res = CollectionSelectResponse(
            id=42,
            created_date="100",
            updated_date="200",
            readonly=True,
            name="X",
            summary=None,
            user=self._user_stub(),
        )
        self.assertEqual(res.created_date, 100)
        self.assertEqual(res.updated_date, 200)

    def test_response_readonly_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_readonly_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly=None,
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly",))
        self.assertEqual(e.get("type"), "bool_type")

    def test_response_readonly_string(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly="not-int",
                name="X",
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("readonly",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_response_readonly_coercion(self):
        res = CollectionSelectResponse(
            id=42,
            created_date=100,
            updated_date=200,
            readonly=1,
            name="X",
            summary=None,
            user=self._user_stub(),
        )
        self.assertEqual(res.readonly, True)

    def test_response_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly=True,
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("name",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_name_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly=True,
                name=None,
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("name",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_name_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly=True,
                name=123,
                summary=None,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("name",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_summary_missing(self):
        res = CollectionSelectResponse(
            id=42,
            created_date=100,
            updated_date=200,
            readonly=True,
            name="X",
            user=self._user_stub(),
        )
        self.assertIsNone(res.summary)

    def test_response_summary_none(self):
        res = CollectionSelectResponse(
            id=42,
            created_date=100,
            updated_date=200,
            readonly=True,
            name="X",
            summary=None,
            user=self._user_stub(),
        )
        self.assertIsNone(res.summary)

    def test_response_summary_string(self):
        res = CollectionSelectResponse(
            id=42,
            created_date=100,
            updated_date=200,
            readonly=True,
            name="X",
            summary="Some text",
            user=self._user_stub(),
        )
        self.assertEqual(res.summary, "Some text")

    def test_response_summary_not_coercion(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly=True,
                name="X",
                summary=123,
                user=self._user_stub(),
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("summary",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_user_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly=True,
                name="X",
                summary=None,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_user_none(self):
        with self.assertRaises(ValidationError) as ctx:
            CollectionSelectResponse(
                id=42,
                created_date=100,
                updated_date=200,
                readonly=True,
                name="X",
                summary=None,
                user=None,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("user",))
        self.assertEqual(e.get("type"), "model_type")
