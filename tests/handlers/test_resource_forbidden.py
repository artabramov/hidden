# tests/handlers/test_resource_forbidden.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ResourceForbiddenError
from app.handlers.resource_forbidden import resource_forbidden_handler


class TestResourceForbiddenHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_403(self):
        request = MagicMock()
        exc = ResourceForbiddenError()

        response = await resource_forbidden_handler(request, exc)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
