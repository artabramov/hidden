# tests/handlers/test_resource_not_found.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ResourceNotFoundError
from app.handlers.resource_not_found import resource_not_found_handler


class TestResourceNotFoundHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_404(self):
        request = MagicMock()
        exc = ResourceNotFoundError()

        response = await resource_not_found_handler(request, exc)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
