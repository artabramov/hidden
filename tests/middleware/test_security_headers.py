# tests/middleware/test_security_headers.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock

from starlette.responses import Response

from app.middleware.security_headers import security_headers_middleware


class TestSecurityHeadersMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_adds_headers(self):
        req = MagicMock()
        inner = AsyncMock(return_value=Response(status_code=200))

        resp = await security_headers_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(resp.headers["X-Frame-Options"], "DENY")
        self.assertEqual(resp.headers["Referrer-Policy"], "no-referrer")
