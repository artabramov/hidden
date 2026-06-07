# tests/schemas/test_file_tag_delete.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.schemas.file_tag_delete import FILE_TAG_DELETE_ERRORS


class TestFileTagDeleteErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(FILE_TAG_DELETE_ERRORS),
            {401, 403, 404, 422, 423, 503},
        )
