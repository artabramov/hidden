# tests/test_errors.py
# SPDX-License-Identifier: Apache-2.0

import unittest

from app.errors import (
    BadGatewayError,
    InternalServerError,
    ServiceUnavailableError,
    UnauthorizedError,
)


class TestErrors(unittest.TestCase):
    def test_errors_are_distinct_exceptions(self):
        errors = (
            UnauthorizedError,
            InternalServerError,
            BadGatewayError,
            ServiceUnavailableError,
        )

        for error in errors:
            with self.subTest(error=error.__name__):
                self.assertTrue(issubclass(error, Exception))
                with self.assertRaises(error):
                    raise error("detail")

        self.assertEqual(len(set(errors)), len(errors))
