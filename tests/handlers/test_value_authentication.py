# tests/handlers/test_value_authentication.py
# SPDX-License-Identifier: GPL-3.0-only

import json
import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ValueAuthenticationError
from app.handlers.value_authentication import value_authentication_handler


class TestValueAuthenticationHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_422_with_detail_payload(self):
        request = MagicMock()
        exc = ValueAuthenticationError(
            field="username",
            input_value="admin",
        )

        response = await value_authentication_handler(request, exc)

        self.assertEqual(
            response.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        payload = json.loads(response.body.decode())
        self.assertEqual(payload, {"detail": exc.detail})
