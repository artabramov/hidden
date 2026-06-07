# tests/paths/test_variable_key.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from fastapi import HTTPException, status

from app.paths.variable_key import get_variable_key


class TestVariableKeyFromRoute(unittest.TestCase):
    def test_builds_valid_path_request(self):
        out = get_variable_key(
            namespace="thumbnails",
            variable_key="max_width",
        )

        self.assertEqual(out.namespace, "thumbnails")
        self.assertEqual(out.variable_key, "max_width")

    def test_applies_path_validation(self):
        with self.assertRaises(HTTPException) as cm:
            get_variable_key(
                namespace="",
                variable_key="k",
            )

        self.assertEqual(
            cm.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            cm.exception.detail[0]["loc"],
            ["path", "namespace"],
        )

    def test_normalizes_case_via_schema(self):
        out = get_variable_key(
            namespace="NS",
            variable_key="KEY",
        )

        self.assertEqual(out.namespace, "ns")
        self.assertEqual(out.variable_key, "key")

    def test_rejects_invalid_segment_characters(self):
        with self.assertRaises(HTTPException) as cm:
            get_variable_key(
                namespace="a/b",
                variable_key="k",
            )

        self.assertEqual(
            cm.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            cm.exception.detail[0]["loc"],
            ["path", "namespace"],
        )

    def test_strips_whitespace_via_schema(self):
        out = get_variable_key(
            namespace="  NS  ",
            variable_key="  KEY  ",
        )

        self.assertEqual(out.namespace, "ns")
        self.assertEqual(out.variable_key, "key")
