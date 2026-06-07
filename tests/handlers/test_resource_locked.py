# tests/handlers/test_resource_locked.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ResourceLockedError
from app.handlers.resource_locked import resource_locked_handler


class TestResourceLockedHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_423(self):
        request = MagicMock()
        exc = ResourceLockedError()

        response = await resource_locked_handler(request, exc)

        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
