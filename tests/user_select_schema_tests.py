import unittest
from pydantic import ValidationError
from app.schemas.user_select import UserSelectResponse


class UserSelectSchemaTest(unittest.TestCase):

    def test_response_correct(self):
        res = UserSelectResponse(
            id=42,
            created_date=100,
            last_login_date=200,
            role="reader",
            active=True,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            summary=None,
            has_thumbnail=False,
        )
        self.assertEqual(res.id, 42)
        self.assertEqual(res.created_date, 100)
        self.assertEqual(res.last_login_date, 200)
        self.assertEqual(res.role, "reader")
        self.assertEqual(res.active, True)
        self.assertEqual(res.username, "johndoe")
        self.assertEqual(res.first_name, "John")
        self.assertEqual(res.last_name, "Doe")
        self.assertIsNone(res.summary)
        self.assertFalse(res.has_thumbnail)

    def test_response_id_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_id_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=None,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_type")

    def test_response_id_string(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id="not-int",
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("id",))
        self.assertEqual(e.get("type"), "int_parsing")

    def test_response_id_coercion(self):
        res = UserSelectResponse(
            id="42",
            created_date=100,
            last_login_date=200,
            role="reader",
            active=True,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            summary=None,
            has_thumbnail=False,
        )
        self.assertEqual(res.id, 42)

    def test_response_timestamps_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "missing")

        self.assertEqual(errs[1].get("loc"), ("last_login_date",))
        self.assertEqual(errs[1].get("type"), "missing")

    def test_response_timestamps_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=None,
                last_login_date=None,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_type")

        self.assertEqual(errs[1].get("loc"), ("last_login_date",))
        self.assertEqual(errs[1].get("type"), "int_type")

    def test_response_timestamps_string(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date="not-int",
                last_login_date="not-int",
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 2)

        self.assertEqual(errs[0].get("loc"), ("created_date",))
        self.assertEqual(errs[0].get("type"), "int_parsing")

        self.assertEqual(errs[1].get("loc"), ("last_login_date",))
        self.assertEqual(errs[1].get("type"), "int_parsing")

    def test_response_timestamps_coercion(self):
        res = UserSelectResponse(
            id=42,
            created_date="100",
            last_login_date="200",
            role="reader",
            active=True,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            summary=None,
            has_thumbnail=False,
        )
        self.assertEqual(res.created_date, 100)
        self.assertEqual(res.last_login_date, 200)

    def test_response_role_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_role_string_empty(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_response_role_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="dummy",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("role",))
        self.assertEqual(e.get("type"), "literal_error")

    def test_response_role_literal(self):
        roles = ["reader", "writer", "editor", "admin"]
        for role in roles:
            res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role=role,
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )
            self.assertEqual(res.role, role)

    def test_response_active_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_active_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=None,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "bool_type")

    def test_response_active_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active="dummy",
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("active",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_response_active_string_0(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active="0",
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
        )
        self.assertEqual(res.active, False)

    def test_response_active_string_1(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active="1",
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
        )
        self.assertEqual(res.active, True)

    def test_response_active_string_true(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active="true",
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
        )
        self.assertEqual(res.active, True)

    def test_response_active_string_false(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active="false",
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
        )
        self.assertEqual(res.active, False)

    def test_response_username_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_username_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username=None,
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("username",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_first_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_first_name_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="john Doe",
                first_name=None,
                last_name="Doe",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("first_name",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_last_name_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_last_name_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="john Doe",
                first_name="John",
                last_name=None,
                summary=None,
                has_thumbnail=False,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("last_name",))
        self.assertEqual(e.get("type"), "string_type")

    def test_response_summary_missing(self):
        res = UserSelectResponse(
            id=42,
            created_date=100,
            last_login_date=200,
            role="reader",
            active=True,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            has_thumbnail=False,
        )
        self.assertIsNone(res.summary)

    def test_response_summary_none(self):
        res = UserSelectResponse(
            id=42,
            created_date=100,
            last_login_date=200,
            role="reader",
            active=True,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            summary=None,
            has_thumbnail=False,
        )
        self.assertIsNone(res.summary)

    def test_response_summary_string(self):
        res = UserSelectResponse(
            id=42,
            created_date=100,
            last_login_date=200,
            role="reader",
            active=True,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            summary="Hello",
            has_thumbnail=False,
        )
        self.assertEqual(res.summary, "Hello")

    def test_response_has_thumbnail_missing(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("has_thumbnail",))
        self.assertEqual(e.get("type"), "missing")

    def test_response_has_thumbnail_none(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail=None,
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("has_thumbnail",))
        self.assertEqual(e.get("type"), "bool_type")

    def test_response_has_thumbnail_string_dummy(self):
        with self.assertRaises(ValidationError) as ctx:
            UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail="dummy",
            )

        errs = ctx.exception.errors()
        self.assertEqual(len(errs), 1)

        e = errs[0]
        self.assertEqual(e.get("loc"), ("has_thumbnail",))
        self.assertEqual(e.get("type"), "bool_parsing")

    def test_response_has_thumbnail_string_0(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail="0",
        )
        self.assertEqual(res.has_thumbnail, False)

    def test_response_has_thumbnail_string_1(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail="1",
        )
        self.assertEqual(res.has_thumbnail, True)

    def test_response_has_thumbnail_string_true(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail="true",
        )
        self.assertEqual(res.has_thumbnail, True)

    def test_response_has_thumbnail_string_false(self):
        res = UserSelectResponse(
                id=42,
                created_date=100,
                last_login_date=200,
                role="reader",
                active=True,
                username="johndoe",
                first_name="John",
                last_name="Doe",
                summary=None,
                has_thumbnail="false",
        )
        self.assertEqual(res.has_thumbnail, False)
