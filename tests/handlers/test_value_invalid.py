# tests/handlers/test_value_invalid.py
# SPDX-License-Identifier: GPL-3.0-only

import json
import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ValueInvalidError
from app.handlers.value_invalid import value_invalid_handler


class TestValueInvalidHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_422_with_detail_payload(self):
        request = MagicMock()
        exc = ValueInvalidError(
            field="username",
            input_value="bad",
        )

        response = await value_invalid_handler(request, exc)

        self.assertEqual(
            response.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        payload = json.loads(response.body.decode())
        self.assertEqual(payload, {"detail": exc.detail})
