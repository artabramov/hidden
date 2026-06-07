# tests/handlers/test_value_conflict.py
# SPDX-License-Identifier: SSPL-1.0

import json
import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ValueConflictError
from app.handlers.value_conflict import value_conflict_handler


class TestValueConflictHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_422_with_detail_payload(self):
        request = MagicMock()
        exc = ValueConflictError(
            field="username",
            input_value="existing",
        )

        response = await value_conflict_handler(request, exc)

        self.assertEqual(
            response.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        payload = json.loads(response.body.decode())
        self.assertEqual(payload, {"detail": exc.detail})
