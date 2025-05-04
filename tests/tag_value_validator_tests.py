import unittest
from app.validators.tag_value_validator import tag_value_validate


class TagValueValidatorTest(unittest.TestCase):

    def test_tag_value_none(self):
        tag_value = tag_value_validate(None)
        self.assertIsNone(tag_value)

    def test_tag_value_empty(self):
        tag_value = tag_value_validate("")
        self.assertIsNone(tag_value)

    def test_tag_value_whitespaces(self):
        tag_value = tag_value_validate(" ")
        self.assertIsNone(tag_value)

    def test_tag_value_str(self):
        tag_value = tag_value_validate(" TAG ")
        self.assertEqual(tag_value, "tag")


if __name__ == "__main__":
    unittest.main()
