# tests/dependencies/test_variable_namespace.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from fastapi import HTTPException, status

from app.paths.variable_namespace import get_variable_namespace


class TestVariableNamespaceFromRoute(unittest.TestCase):

    def test_builds_valid_namespace_request(self):
        out = get_variable_namespace(namespace="thumbnails")

        self.assertEqual(out.namespace, "thumbnails")

    def test_applies_path_validation(self):
        with self.assertRaises(HTTPException) as cm:
            get_variable_namespace(namespace="")

        self.assertEqual(
            cm.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            cm.exception.detail[0]["loc"],
            ["path", "namespace"],
        )

    def test_normalizes_case_via_schema(self):
        out = get_variable_namespace(namespace="NS")

        self.assertEqual(out.namespace, "ns")

    def test_rejects_invalid_segment_characters(self):
        with self.assertRaises(HTTPException) as cm:
            get_variable_namespace(namespace="a/b")

        self.assertEqual(
            cm.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            cm.exception.detail[0]["loc"],
            ["path", "namespace"],
        )

    def test_strips_whitespace_via_schema(self):
        out = get_variable_namespace(namespace="  NS  ")

        self.assertEqual(out.namespace, "ns")
