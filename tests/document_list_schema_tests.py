import unittest
from pydantic import ValidationError
from app.schemas.document_list_schema import DocumentListRequest
from app.config import get_config

cfg = get_config()


class TestDocumentListRequest(unittest.TestCase):

    def test_correct(self):
        data = {
            "user_id__eq": 123,
            "collection_id__eq": 234,
            "tag_value__eq": "tag",
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.user_id__eq, 123)
        self.assertEqual(schema.collection_id__eq, 234)
        self.assertEqual(schema.tag_value__eq, "tag")
        self.assertEqual(schema.offset, 0)
        self.assertEqual(schema.limit, 10)
        self.assertEqual(schema.order_by, "id")
        self.assertEqual(schema.order, "asc")

    def test_user_id_none(self):
        data = {
            "user_id__eq": None,
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertIsNone(schema.user_id__eq)

    def test_user_id_int(self):
        data = {
            "user_id__eq": 123,
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.user_id__eq, 123)

    def test_user_id_str(self):
        data = {
            "user_id__eq": "id",
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_collection_id_none(self):
        data = {
            "collection_id__eq": None,
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertIsNone(schema.collection_id__eq)

    def test_collection_id_int(self):
        data = {
            "collection_id__eq": 123,
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.collection_id__eq, 123)

    def test_collection_id_str(self):
        data = {
            "collection_id__eq": "id",
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_tag_value_none(self):
        data = {
            "tag_value__eq": None,
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertIsNone(schema.tag_value__eq)

    def test_tag_value_str(self):
        data = {
            "tag_value__eq": "TAG",
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.tag_value__eq, "tag")

    def test_offset_none(self):
        data = {
            "offset": None,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertIsNone(schema.offset)

    def test_offset_str(self):
        data = {
            "offset": "dummy",
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_offset_too_low(self):
        data = {
            "offset": -1,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_offset_min(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.offset, 0)

    def test_limit_none(self):
        data = {
            "offset": 0,
            "limit": None,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertIsNone(schema.limit)

    def test_limit_str(self):
        data = {
            "offset": 0,
            "limit": "dummy",
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_limit_too_low(self):
        data = {
            "offset": 0,
            "limit": 0,
            "order_by": "id",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_limit_min(self):
        data = {
            "offset": 0,
            "limit": 1,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.limit, 1)

    def test_order_by_none(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": None,
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertIsNone(schema.order_by)

    def test_order_by_invalid(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "dummy",
            "order": "asc"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_order_by_correct(self):
        orders_bys = [
            "id", "user_id", "collection_id", "original_filename_index",
            "document_filesize_index", "document_mimetype_index"]

        for order_by in orders_bys:
            data = {
                "offset": 0,
                "limit": 10,
                "order_by": order_by,
                "order": "asc"
            }
            schema = DocumentListRequest(**data)
            self.assertEqual(schema.order_by, order_by)

    def test_order_none(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": None
        }
        schema = DocumentListRequest(**data)
        self.assertIsNone(schema.order)

    def test_order_invalid(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "dummy"
        }
        with self.assertRaises(ValidationError):
            DocumentListRequest(**data)

    def test_order_asc(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "asc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.order, "asc")

    def test_order_desc(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "desc"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.order, "desc")

    def test_order_rand(self):
        data = {
            "offset": 0,
            "limit": 10,
            "order_by": "id",
            "order": "rand"
        }
        schema = DocumentListRequest(**data)
        self.assertEqual(schema.order, "rand")


if __name__ == "__main__":
    unittest.main()
