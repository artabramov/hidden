# tests/handlers/test_internal_server_error.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import InternalServerError
from app.handlers.internal_server_error import internal_server_error_handler


class TestInternalServerErrorHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_500(self):
        request = MagicMock()
        exc = InternalServerError()

        response = await internal_server_error_handler(request, exc)

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
