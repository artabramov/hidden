# tests/handlers/value_not_found.py
# SPDX-License-Identifier: GPL-3.0-only

import json
import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ValueNotFoundError
from app.handlers.value_not_found import value_not_found_handler


class TestValueNotFoundHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_422_with_detail_payload(self):
        request = MagicMock()
        exc = ValueNotFoundError(
            field="username",
            input_value="missing",
        )

        response = await value_not_found_handler(request, exc)

        self.assertEqual(
            response.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        payload = json.loads(response.body.decode())
        self.assertEqual(payload, {"detail": exc.detail})
