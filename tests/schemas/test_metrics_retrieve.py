# tests/schemas/test_metrics_retrieve.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.schemas.metrics_retrieve import METRICS_RETRIEVE_ERRORS


class TestMetricsRetrieveErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(METRICS_RETRIEVE_ERRORS),
            {401, 403, 503},
        )
