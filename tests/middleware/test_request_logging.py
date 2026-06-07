# tests/middleware/test_request_logging.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from starlette.responses import Response

from app.middleware.request_logging import request_logging_middleware


class TestRequestLoggingMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_logs_start_and_finish(self):
        req = MagicMock()
        req.method = "GET"
        req.url = "http://x/y"
        req.client = MagicMock()
        req.client.host = "10.0.0.1"
        inner = AsyncMock(return_value=Response(status_code=201))

        with (
            patch(
                "app.middleware.request_logging.get_context_var",
                return_value=1000.0,
            ),
            patch(
                "app.middleware.request_logging.time.perf_counter",
                return_value=1000.25,
            ),
            patch(
                "app.middleware.request_logging.logger",
            ) as mock_log,
        ):
            resp = await request_logging_middleware(req, inner)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(mock_log.info.call_count, 2)
        mock_log.error.assert_not_called()

    async def test_no_client_host_logs_none(self):
        req = MagicMock()
        req.method = "POST"
        req.url = "http://x/"
        req.client = None
        inner = AsyncMock(return_value=Response(status_code=200))

        with (
            patch(
                "app.middleware.request_logging.get_context_var",
                return_value=0.0,
            ),
            patch(
                "app.middleware.request_logging.time.perf_counter",
                return_value=0.1,
            ),
            patch("app.middleware.request_logging.logger") as mock_log,
        ):
            await request_logging_middleware(req, inner)

        first = mock_log.info.call_args_list[0]
        self.assertIsNone(first[0][4])

    async def test_inner_exception_logs_error_and_reraises(self):
        req = MagicMock()
        req.method = "GET"
        req.url = "http://x/"
        req.client = None

        async def inner(_r):
            raise ValueError("boom")

        with patch("app.middleware.request_logging.logger") as mock_log:
            with self.assertRaises(ValueError):
                await request_logging_middleware(req, inner)

        mock_log.exception.assert_called_once()
