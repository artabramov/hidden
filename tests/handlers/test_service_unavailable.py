# tests/handlers/test_service_unavailable.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ServiceUnavailableError
from app.handlers.service_unavailable import service_unavailable_handler


class TestServiceUnavailableHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_503_with_retry_after(self):
        request = MagicMock()
        exc = ServiceUnavailableError()

        response = await service_unavailable_handler(request, exc)

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(response.headers.get("Retry-After"), "300")
