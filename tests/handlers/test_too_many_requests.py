# tests/handlers/test_too_many_requests.py
# SPDX-License-Identifier: GPL-3.0-only

import json
import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import TooManyRequestsError
from app.handlers.too_many_requests import too_many_requests_handler


class TestTooManyRequestsHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_429_with_detail_payload(self):
        request = MagicMock()
        exc = TooManyRequestsError()

        response = await too_many_requests_handler(request, exc)

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        payload = json.loads(response.body.decode())
        self.assertEqual(
            payload,
            {"detail": "Too many requests"},
        )
