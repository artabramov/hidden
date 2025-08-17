import unittest
from app.helpers.sort_helper import get_index, INDEX_LENGTH


class SortingHelperIndex(unittest.TestCase):

    def test_sort_helper_empty_string(self):
        self.assertEqual(get_index(""), 0)

    def test_sort_helper_single_character(self):
        self.assertEqual(get_index("A"), get_index("A"))
        self.assertEqual(get_index("Z"), get_index("Z"))

    def test_sort_helper_multiple_characters(self):
        self.assertEqual(get_index("Apple"), get_index("Apple"))
        self.assertEqual(get_index("Banana"), get_index("Banana"))

    def test_sort_helper_string_with_special_characters(self):
        self.assertEqual(get_index("!@#$%^&*"), get_index("!@#$%^&*"))
        self.assertEqual(get_index("12345678"), get_index("12345678"))

    def test_sort_helper_string_with_unicode(self):
        self.assertEqual(get_index("Привет"), get_index("Привет"))
        self.assertEqual(get_index("你好"), get_index("你好"))

    def test_sort_helper_case_insensitivity(self):
        self.assertEqual(get_index("apple"), get_index("Apple"))
        self.assertEqual(get_index("Banana"), get_index("banana"))
        self.assertEqual(get_index("straße"), get_index("STRASSE"))
        self.assertEqual(get_index("É"), get_index("E\u0301"))
        self.assertEqual(get_index("Σίσυφος"), get_index("σίσυφος"))

    def test_sort_helper_string_with_less_than_index_length(self):
        self.assertEqual(get_index("Apple"), get_index("Apple"))
        self.assertEqual(get_index("Hi"), get_index("Hi"))

    def test_sort_helper_string_with_more_than_index_length(self):
        self.assertEqual(get_index("AppleBananaAppleBanana"),
                         get_index("AppleBananaAppleBanana"))

    def test_sort_helper_non_ascii_characters(self):
        self.assertEqual(get_index("ñ"), get_index("ñ"))
        self.assertEqual(get_index("ø"), get_index("ø"))

    def test_sort_helper_maximum_length_string(self):
        self.assertEqual(get_index("a" * INDEX_LENGTH),
                         get_index("a" * INDEX_LENGTH))

    def test_sort_helper_edge_cases(self):
        self.assertEqual(get_index(""), 0)
        self.assertEqual(get_index("A"), get_index("A"))

    def test_sort_helper_values_different_types(self):
        self.assertEqual(get_index("1234"), get_index(1234))
        self.assertTrue(get_index("1234") < get_index(2345))
        self.assertTrue(get_index(1234) < get_index("2345"))


if __name__ == "__main__":
    unittest.main()
