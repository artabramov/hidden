# tests/test_handlers.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock

from app.errors import (
    BadGatewayError,
    InternalServerError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from app.handlers import (
    bad_gateway_handler,
    internal_server_error_handler,
    service_unavailable_handler,
    unauthorized_handler,
)


class TestHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_returns_empty_error_response(self):
        cases = (
            (unauthorized_handler, UnauthorizedError, 401),
            (internal_server_error_handler, InternalServerError, 500),
            (bad_gateway_handler, BadGatewayError, 502),
            (service_unavailable_handler, ServiceUnavailableError, 503),
        )

        for handler, error, status_code in cases:
            with self.subTest(status_code=status_code):
                response = await handler(MagicMock(), error("detail"))

                self.assertEqual(response.status_code, status_code)
                self.assertEqual(response.body, b"")
