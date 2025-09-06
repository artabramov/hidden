import unittest
from pydantic import ValidationError
from app.schemas.user_list import UserListRequest, UserListResponse
from app.schemas.user_select import UserSelectResponse


class UserListSchemasTest(unittest.TestCase):
    def test_request_minimal_valid(self):
        m = UserListRequest(
            offset=0,
            limit=10,
            order_by="id",
            order="asc",
        )
        self.assertEqual(m.offset, 0)
        self.assertEqual(m.limit, 10)
        self.assertEqual(m.order_by, "id")
        self.assertEqual(m.order, "asc")

    def test_string_filters_are_trimmed(self):
        m = UserListRequest(
            username__ilike="  john  ",
            first_name__ilike="  Jane  ",
            last_name__ilike="  Doe ",
            full_name__ilike="  Jane Doe  ",
            offset=0,
            limit=5,
            order_by="username",
            order="desc",
        )
        self.assertEqual(m.username__ilike, "john")
        self.assertEqual(m.first_name__ilike, "Jane")
        self.assertEqual(m.last_name__ilike, "Doe")
        self.assertEqual(m.full_name__ilike, "Jane Doe")

    def test_blank_strings_are_preserved_after_trim(self):
        m = UserListRequest(
            username__ilike="",
            first_name__ilike="   ",
            last_name__ilike="\t",
            full_name__ilike="\n",
            offset=0,
            limit=5,
            order_by="first_name",
            order="asc",
        )
        self.assertEqual(m.username__ilike, "")
        self.assertEqual(m.first_name__ilike, "")
        self.assertEqual(m.last_name__ilike, "")
        self.assertEqual(m.full_name__ilike, "")

    def test_role_literal_enforced(self):
        ok = UserListRequest(
            role__eq="admin",
            offset=0,
            limit=1,
            order_by="id",
            order="asc",
        )
        self.assertEqual(ok.role__eq, "admin")

        with self.assertRaises(ValidationError):
            UserListRequest(role__eq="Admin", offset=0, limit=1, order_by="id", order="asc")

        with self.assertRaises(ValidationError):
            UserListRequest(role__eq=" admin ", offset=0, limit=1, order_by="id", order="asc")

    def test_offset_and_limit_bounds(self):
        with self.assertRaises(ValidationError):
            UserListRequest(offset=-1, limit=10, order_by="id", order="asc")
        with self.assertRaises(ValidationError):
            UserListRequest(offset=0, limit=0, order_by="id", order="asc")
        with self.assertRaises(ValidationError):
            UserListRequest(offset=0, limit=201, order_by="id", order="asc")

    def test_order_by_literal_enforced(self):
        with self.assertRaises(ValidationError):
            UserListRequest(offset=0, limit=10, order_by="unknown", order="asc")

    def test_order_literal_enforced(self):
        with self.assertRaises(ValidationError):
            UserListRequest(offset=0, limit=10, order_by="id", order="up")

    def test_response_valid(self):
        user = UserSelectResponse(
            id=1,
            created_date=1,
            last_login_date=0,
            role="reader",
            active=True,
            username="john",
            first_name="John",
            last_name="Doe",
            summary=None,
            has_thumbnail=False,
        )
        r = UserListResponse(users=[user], users_count=1)
        self.assertEqual(r.users_count, 1)
        self.assertEqual(len(r.users), 1)
        self.assertEqual(r.users[0].username, "john")
