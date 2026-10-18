# tests/middleware/test_security_headers.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock

from app.middleware.security_headers import security_headers_middleware


class TestSecurityHeadersMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_adds_security_headers(self):
        request = MagicMock()
        response = MagicMock()
        response.headers = {}

        async def call_next(received):
            self.assertIs(received, request)
            return response

        result = await security_headers_middleware(request, call_next)

        self.assertIs(result, response)
        self.assertEqual(
            response.headers,
            {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
            },
        )
