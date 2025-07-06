import unittest
from unittest.mock import MagicMock
from app.mixins.meta_mixin import MetaMixin


class TestClass(MetaMixin):

    meta_relationship = "parent_meta"
    parent_meta = [
        MagicMock(meta_key="key1", meta_value="1"),
        MagicMock(meta_key="key2", meta_value="2"),
        MagicMock(meta_key="key3", meta_value="3"),
        MagicMock(meta_key="key4", meta_value="4")]


class MetaMixinTest(unittest.IsolatedAsyncioTestCase):

    def test_meta_relationship(self):
        relationship_mock = MagicMock()
        relationship_mock.back_populates = "parent_meta"

        relationships_mock = MagicMock()
        relationships_mock._data.values.return_value = [relationship_mock]

        mapper_mock = MagicMock()
        mapper_mock.relationships = relationships_mock

        meta_mock = MagicMock()
        meta_mock.__mapper__ = mapper_mock

        mixin = MetaMixin()
        mixin._meta = meta_mock

        result = mixin.meta_relationship
        self.assertEqual(result, relationship_mock.back_populates)

    def test_get_meta(self):
        test = TestClass()
        result = test.get_meta("key2")

        self.assertEqual(result, TestClass.parent_meta[1])
        self.assertEqual(result.meta_key, "key2")
        self.assertEqual(result.meta_value, "2")

    def test_set_meta(self):
        test = TestClass()
        test.set_meta("key1", "11")

        self.assertEqual(test.parent_meta[0].meta_value, "11")
        self.assertEqual(test.parent_meta[1].meta_value, "2")
        self.assertEqual(test.parent_meta[2].meta_value, "3")
        self.assertEqual(test.parent_meta[3].meta_value, "4")


if __name__ == "__main__":
    unittest.main()
