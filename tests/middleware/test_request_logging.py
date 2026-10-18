# tests/middleware/test_request_logging.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock, patch

from app.context import reset_context, set_context_var
from app.middleware.request_logging import request_logging_middleware


class TestRequestLoggingMiddleware(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        reset_context()

    async def test_logs_successful_request(self):
        request = MagicMock()
        request.method = "GET"
        request.url = "http://example/"
        request.client.host = "127.0.0.1"
        response = MagicMock()
        response.status_code = 204
        set_context_var("request_start_time", 10.0)

        async def call_next(received):
            self.assertIs(received, request)
            return response

        with patch(
            "app.middleware.request_logging.time.perf_counter",
            return_value=10.5,
        ):
            with self.assertLogs(
                "app.middleware.request_logging",
                level="INFO",
            ) as logs:
                result = await request_logging_middleware(
                    request,
                    call_next,
                )

        self.assertIs(result, response)
        self.assertIn(
            "msg=request_started method=GET "
            "url=http://example/ client=127.0.0.1",
            logs.output[0],
        )
        self.assertIn(
            "msg=request_finished status_code=204 "
            "elapsed_time=0.500000",
            logs.output[1],
        )

    async def test_logs_missing_client_as_none(self):
        request = MagicMock()
        request.method = "POST"
        request.url = "http://example/mount"
        request.client = None
        response = MagicMock()
        response.status_code = 200
        set_context_var("request_start_time", 1.0)

        async def call_next(received):
            return response

        with patch(
            "app.middleware.request_logging.time.perf_counter",
            return_value=1.0,
        ):
            with self.assertLogs(
                "app.middleware.request_logging",
                level="INFO",
            ) as logs:
                await request_logging_middleware(request, call_next)

        self.assertIn(
            "msg=request_started method=POST "
            "url=http://example/mount client=None",
            logs.output[0],
        )

    async def test_logs_and_reraises_request_failure(self):
        request = MagicMock()
        request.method = "POST"
        request.url = "http://example/mount"
        request.client.host = "127.0.0.1"

        async def call_next(received):
            raise RuntimeError("boom")

        with self.assertLogs(
            "app.middleware.request_logging",
            level="INFO",
        ) as logs:
            with self.assertRaises(RuntimeError):
                await request_logging_middleware(request, call_next)

        self.assertIn("msg=request_started", logs.output[0])
        self.assertIn("msg=request_failed", logs.output[1])
        self.assertFalse(
            any("msg=request_finished" in line for line in logs.output)
        )
