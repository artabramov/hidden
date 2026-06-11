# tests/test_openapi.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from app.openapi import TAGS_METADATA


class TestOpenAPITags(unittest.TestCase):

    def test_tags_is_list_of_dicts(self):
        self.assertIsInstance(TAGS_METADATA, list)

        for tag in TAGS_METADATA:
            self.assertIsInstance(tag, dict)

    def test_each_tag_has_required_fields(self):
        for tag in TAGS_METADATA:
            self.assertIn("name", tag)
            self.assertIn("description", tag)

            self.assertIsInstance(tag["name"], str)
            self.assertIsInstance(tag["description"], str)

            self.assertTrue(tag["name"])
            self.assertTrue(tag["description"])

    def test_tag_names_are_unique(self):
        names = [tag["name"] for tag in TAGS_METADATA]
        self.assertEqual(len(names), len(set(names)))

    def test_expected_tags_present(self):
        expected = {
            "Initialization",
            "Authentication",
            "Users",
            "Folders",
            "Files",
            "Tags",
            "Comments",
            "Variables",
            "Services",
        }

        actual = {tag["name"] for tag in TAGS_METADATA}
        self.assertEqual(actual, expected)
