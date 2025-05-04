import unittest
from pydantic import ValidationError
from app.schemas.user_list_schema import UserListRequest
from app.config import get_config

cfg = get_config()


class TestUserListRequest(unittest.TestCase):

    def test_request_correct(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = UserListRequest(**data)
        self.assertEqual(schema.offset, 0)
        self.assertEqual(schema.limit, 10)
        self.assertEqual(schema.order_by, "id")
        self.assertEqual(schema.order, "asc")

    def test_offset_none(self):
        data = {
            "offset": None,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = UserListRequest(**data)
        self.assertIsNone(schema.offset)

    def test_offset_str(self):
        data = {
            "offset": "dummy",
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            UserListRequest(**data)

    def test_offset_too_low(self):
        data = {
            "offset": -1,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            UserListRequest(**data)

    def test_offset_min(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = UserListRequest(**data)
        self.assertEqual(schema.offset, 0)

    def test_limit_none(self):
        data = {
            "offset": 0,
            "limit": None,
            "order_by": "id",
            "order": "asc"
        }
        schema = UserListRequest(**data)
        self.assertIsNone(schema.limit)

    def test_limit_str(self):
        data = {
            "offset": 0,
            "limit": "dummy",
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            UserListRequest(**data)

    def test_limit_too_low(self):
        data = {
            "offset": 0,
            "limit": 0,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            UserListRequest(**data)

    def test_limit_min(self):
        data = {
            "offset": 0,
            "limit": 1,
            "order_by": "id",
            "order": "asc"
        }
        schema = UserListRequest(**data)
        self.assertEqual(schema.limit, 1)

    def test_order_by_none(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": None,
            "order": "asc"
        }
        schema = UserListRequest(**data)
        self.assertIsNone(schema.order_by)

    def test_order_by_invalid(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "dummy",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            UserListRequest(**data)

    def test_order_by_correct(self):
        orders_bys = ["id", "username_index", "first_name_index",
                      "last_name_index"]

        for order_by in orders_bys:
            data = {
                "offset": 0,
                "limit": 10,
                "order_by": order_by,
                "order": "asc"
            }
            schema = UserListRequest(**data)
            self.assertEqual(schema.order_by, order_by)

    def test_order_none(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": None
        }
        schema = UserListRequest(**data)
        self.assertIsNone(schema.order)

    def test_order_invalid(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "dummy"
        }
        with self.assertRaises(ValidationError):
            UserListRequest(**data)

    def test_order_asc(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = UserListRequest(**data)
        self.assertEqual(schema.order, "asc")

    def test_order_desc(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "desc"
        }
        schema = UserListRequest(**data)
        self.assertEqual(schema.order, "desc")

    def test_order_rand(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "rand"
        }
        schema = UserListRequest(**data)
        self.assertEqual(schema.order, "rand")


if __name__ == "__main__":
    unittest.main()
