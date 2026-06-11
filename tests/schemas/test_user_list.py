# tests/schemas/test_user_list.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.user_list import (
    UserListRequest,
    UserListResponse,
)


class TestUserListRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = UserListRequest(
            created_at__ge=1,
            created_at__le=2,
            last_authenticated_at__ge=3,
            last_authenticated_at__le=4,
            is_active__eq=True,
            role__eq="admin",
            username__ilike="test",
            display_name__ilike="User",
            offset=10,
            limit=20,
            order_by="username",
            order="asc",
        )

        self.assertEqual(req.created_at__ge, 1)
        self.assertEqual(req.created_at__le, 2)
        self.assertEqual(req.last_authenticated_at__ge, 3)
        self.assertEqual(req.last_authenticated_at__le, 4)
        self.assertTrue(req.is_active__eq)
        self.assertEqual(req.role__eq, "admin")
        self.assertEqual(req.username__ilike, "test")
        self.assertEqual(req.display_name__ilike, "User")
        self.assertEqual(req.offset, 10)
        self.assertEqual(req.limit, 20)
        self.assertEqual(req.order_by, "username")
        self.assertEqual(req.order, "asc")

    def test_uses_defaults(self):
        req = UserListRequest()

        self.assertIsNone(req.created_at__ge)
        self.assertIsNone(req.created_at__le)
        self.assertIsNone(req.last_authenticated_at__ge)
        self.assertIsNone(req.last_authenticated_at__le)
        self.assertIsNone(req.is_active__eq)
        self.assertIsNone(req.role__eq)
        self.assertIsNone(req.username__ilike)
        self.assertIsNone(req.display_name__ilike)
        self.assertEqual(req.offset, 0)
        self.assertEqual(req.limit, 50)
        self.assertEqual(req.order_by, "id")
        self.assertEqual(req.order, "desc")

    def test_strips_whitespace(self):
        req = UserListRequest(
            username__ilike="  test  ",
            display_name__ilike="  User  ",
        )

        self.assertEqual(req.username__ilike, "test")
        self.assertEqual(req.display_name__ilike, "User")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserListRequest(other=1)

    def test_created_at_ge_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(created_at__ge=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("created_at__ge",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_created_at_le_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(created_at__le=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("created_at__le",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_last_authenticated_at_ge_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(last_authenticated_at__ge=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("last_authenticated_at__ge",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_last_authenticated_at_le_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(last_authenticated_at__le=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("last_authenticated_at__le",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_offset_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(offset=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("offset",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_limit_rejects_zero(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(limit=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("limit",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_limit_rejects_value_above_maximum(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(limit=501)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("limit",))
        self.assertEqual(error["type"], "less_than_equal")

    def test_role_eq_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(role__eq="owner")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("role__eq",))
        self.assertEqual(error["type"], "literal_error")

    def test_order_by_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(order_by="email")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("order_by",))
        self.assertEqual(error["type"], "literal_error")

    def test_order_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListRequest(order="up")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("order",))
        self.assertEqual(error["type"], "literal_error")

    def test_accepts_username_ilike(self) -> None:
        data = UserListRequest(username__ilike="john")
        self.assertEqual(data.username__ilike, "john")

    def test_accepts_display_name_ilike(self) -> None:
        data = UserListRequest(display_name__ilike="doe")
        self.assertEqual(data.display_name__ilike, "doe")

    def test_accepts_empty_username_ilike(self) -> None:
        data = UserListRequest(username__ilike="")
        self.assertEqual(data.username__ilike, "")

    def test_accepts_empty_display_name_ilike(self) -> None:
        data = UserListRequest(display_name__ilike="")
        self.assertEqual(data.display_name__ilike, "")

    def test_strips_username_ilike(self) -> None:
        data = UserListRequest(username__ilike="  john  ")
        self.assertEqual(data.username__ilike, "john")

    def test_strips_display_name_ilike(self) -> None:
        data = UserListRequest(display_name__ilike="  doe  ")
        self.assertEqual(data.display_name__ilike, "doe")


class TestUserListResponse(unittest.TestCase):

    def test_accepts_valid_payload(self):
        resp = UserListResponse(
            users=[
                {
                    "user_id": 1,
                    "created_at": 100,
                    "last_authenticated_at": 200,
                    "role": "admin",
                    "is_active": True,
                    "username": "testuser",
                    "display_name": "Test User",
                    "summary": "Profile summary.",
                }
            ],
            users_count=1,
        )

        self.assertEqual(len(resp.users), 1)
        self.assertEqual(resp.users_count, 1)
        self.assertEqual(resp.users[0].user_id, 1)
        self.assertEqual(resp.users[0].username, "testuser")

    def test_accepts_empty_users(self):
        resp = UserListResponse(
            users=[],
            users_count=0,
        )

        self.assertEqual(resp.users, [])
        self.assertEqual(resp.users_count, 0)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            UserListResponse(
                users=[],
                users_count=0,
                other=1,
            )

    def test_users_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserListResponse(users_count=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("users",))
        self.assertEqual(error["type"], "missing")

    def test_users_count_required(self):
        with self.assertRaises(ValidationError) as cm:
            UserListResponse(users=[])

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("users_count",))
        self.assertEqual(error["type"], "missing")

    def test_users_count_rejects_negative_value(self):
        with self.assertRaises(ValidationError) as cm:
            UserListResponse(
                users=[],
                users_count=-1,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("users_count",))
        self.assertEqual(error["type"], "greater_than_equal")
