# tests/schemas/test_folder_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from app.schemas.folder_delete import FOLDER_DELETE_ERRORS


class TestFolderDeleteErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(FOLDER_DELETE_ERRORS),
            {401, 403, 404, 409, 422, 423, 503},
        )
