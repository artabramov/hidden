# tests/middleware/test_request_context.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock, patch

from app.context import get_context_var, reset_context
from app.middleware.request_context import (
    request_context_middleware,
    resolve_request_uuid,
)


class TestResolveRequestUuid(unittest.TestCase):
    def test_generates_identifier_when_header_is_missing(self):
        with patch(
            "app.middleware.request_context.uuid.uuid4",
        ) as uuid4:
            uuid4.return_value.hex = "generated-id"

            self.assertEqual(resolve_request_uuid(None), "generated-id")

    def test_keeps_valid_identifier(self):
        self.assertEqual(
            resolve_request_uuid("  Ab-1_Z  "),
            "Ab-1_Z",
        )
        self.assertEqual(
            resolve_request_uuid("a" * 64),
            "a" * 64,
        )

    def test_generates_identifier_when_header_is_invalid(self):
        cases = ["", "   ", "a" * 65, "bad id", "id.with.dot"]

        with patch(
            "app.middleware.request_context.uuid.uuid4",
        ) as uuid4:
            uuid4.return_value.hex = "generated-id"

            for value in cases:
                with self.subTest(value=value):
                    self.assertEqual(
                        resolve_request_uuid(value),
                        "generated-id",
                    )


class TestRequestContextMiddleware(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        reset_context()

    async def test_sets_context_and_response_header(self):
        request = MagicMock()
        request.headers = {"X-Request-ID": "  request-id_1  "}
        response = MagicMock()
        response.headers = {}
        seen = {}

        async def call_next(received):
            self.assertIs(received, request)
            seen["request_uuid"] = get_context_var("request_uuid")
            seen["request_start_time"] = get_context_var(
                "request_start_time",
            )
            return response

        with patch(
            "app.middleware.request_context.time.perf_counter",
            return_value=12.5,
        ):
            result = await request_context_middleware(request, call_next)

        self.assertIs(result, response)
        self.assertEqual(seen["request_uuid"], "request-id_1")
        self.assertEqual(seen["request_start_time"], 12.5)
        self.assertEqual(
            response.headers["X-Request-ID"],
            "request-id_1",
        )
        self.assertIsNone(get_context_var("request_uuid"))
        self.assertIsNone(get_context_var("request_start_time"))

    async def test_generates_identifier_when_header_is_missing(self):
        request = MagicMock()
        request.headers = {}
        response = MagicMock()
        response.headers = {}

        async def call_next(received):
            return response

        with patch(
            "app.middleware.request_context.uuid.uuid4",
        ) as uuid4:
            uuid4.return_value.hex = "generated-id"
            result = await request_context_middleware(request, call_next)

        self.assertIs(result, response)
        self.assertEqual(response.headers["X-Request-ID"], "generated-id")
        self.assertIsNone(get_context_var("request_uuid"))

    async def test_resets_context_when_request_fails(self):
        request = MagicMock()
        request.headers = {"X-Request-ID": "request-id_1"}

        async def call_next(received):
            self.assertEqual(
                get_context_var("request_uuid"),
                "request-id_1",
            )
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            await request_context_middleware(request, call_next)

        self.assertIsNone(get_context_var("request_uuid"))
        self.assertIsNone(get_context_var("request_start_time"))
