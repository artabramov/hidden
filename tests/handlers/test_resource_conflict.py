# tests/handlers/test_resource_conflict.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock

from fastapi import status

from app.errors import ResourceConflictError
from app.handlers.resource_conflict import resource_conflict_handler


class TestResourceConflictHandler(unittest.IsolatedAsyncioTestCase):
    async def test_returns_409(self):
        request = MagicMock()
        exc = ResourceConflictError()

        response = await resource_conflict_handler(request, exc)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
