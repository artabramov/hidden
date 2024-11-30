import unittest
from app.helpers.tag_helper import extract_tag_values


class TagHelperTestCase(unittest.TestCase):

    def test_extract_tag_values_multiple_tags(self):
        """
        Test that extract_tag_values handles multiple tags correctly.
        """
        source_string = "tag1, tag2, tag3, tag1"
        result = extract_tag_values(source_string)
        self.assertCountEqual(result, ["tag1", "tag2", "tag3"])

    def test_extract_tag_values_no_duplicates(self):
        """
        Test that extract_tag_values works correctly with no duplicates.
        """
        source_string = "tag1, tag2, tag3"
        result = extract_tag_values(source_string)
        self.assertCountEqual(result, ["tag1", "tag2", "tag3"])

    def test_extract_tag_values_empty_input(self):
        """
        Test that extract_tag_values returns an empty list for empty
        input.
        """
        source_string = ""
        result = extract_tag_values(source_string)
        self.assertEqual(result, [])

    def test_extract_tag_values_none_input(self):
        """
        Test that extract_tag_values returns an empty list for None
        input.
        """
        source_string = None
        result = extract_tag_values(source_string)
        self.assertEqual(result, [])

    def test_extract_tag_values_whitespace_input(self):
        """Test that extract_tag_values strips whitespace from tags."""
        source_string = "  tag1 ,  tag2   ,  tag3  "
        result = extract_tag_values(source_string)
        self.assertCountEqual(result, ["tag1", "tag2", "tag3"])

    def test_extract_tag_values_empty_tags(self):
        """
        Test that extract_tag_values ignores empty tags (e.g., ',,').
        """
        source_string = ",,,tag1,,,,tag2,,"
        result = extract_tag_values(source_string)
        self.assertCountEqual(result, ["tag1", "tag2"])


if __name__ == "__main__":
    unittest.main()
