# tests/routers/test_metrics_retrieve.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, patch

from fastapi.responses import JSONResponse

from app.routers.metrics_retrieve import retrieve_metrics_router


class TestMetricsRetrieveRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_200_and_calls_service(self):
        session = AsyncMock()
        user = object()

        expected_metrics = {"ok": True}

        with patch(
            "app.routers.metrics_retrieve.retrieve_metrics",
            new=AsyncMock(return_value=expected_metrics),
        ) as service_mock:
            response = await retrieve_metrics_router(
                session=session,
                current_user=user,
            )

        service_mock.assert_awaited_once_with(session)

        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'{"ok":true}')

    async def test_passes_session_to_service(self):
        session = AsyncMock()
        user = object()

        with patch(
            "app.routers.metrics_retrieve.retrieve_metrics",
            new=AsyncMock(return_value={}),
        ) as service_mock:
            await retrieve_metrics_router(
                session=session,
                current_user=user,
            )

        args, _ = service_mock.await_args
        self.assertIs(args[0], session)
