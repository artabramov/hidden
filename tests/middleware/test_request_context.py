# tests/middleware/test_request_context.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from starlette.responses import Response

from app.middleware.request_context import (
    request_context_middleware,
    resolve_request_uuid,
)


class TestResolveRequestUuid(unittest.TestCase):
    @patch("app.middleware.request_context.uuid.uuid4")
    def test_none_generates_uuid(self, mock_uuid: MagicMock) -> None:
        u = uuid.UUID("12345678-1234-5678-1234-567812345678")
        mock_uuid.return_value = u

        self.assertEqual(resolve_request_uuid(None), u.hex)

    def test_valid_header_preserved(self) -> None:
        self.assertEqual(resolve_request_uuid("abc-XYZ_09"), "abc-XYZ_09")

    def test_whitespace_trimmed(self) -> None:
        self.assertEqual(resolve_request_uuid("  ok-id  "), "ok-id")

    @patch("app.middleware.request_context.uuid.uuid4")
    def test_empty_after_strip_generates(self, mock_uuid: MagicMock) -> None:
        u = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        mock_uuid.return_value = u

        self.assertEqual(resolve_request_uuid("   "), u.hex)

    @patch("app.middleware.request_context.uuid.uuid4")
    def test_too_long_generates(self, mock_uuid: MagicMock) -> None:
        u = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
        mock_uuid.return_value = u

        long_val = "a" * 65
        self.assertEqual(resolve_request_uuid(long_val), u.hex)

    @patch("app.middleware.request_context.uuid.uuid4")
    def test_invalid_chars_generates(self, mock_uuid: MagicMock) -> None:
        u = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
        mock_uuid.return_value = u

        self.assertEqual(resolve_request_uuid("bad id!"), u.hex)


class TestRequestContextMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_sets_response_header_and_calls_next(self):
        req = MagicMock()
        req.headers.get = MagicMock(return_value="corr-id-1")
        inner = AsyncMock(return_value=Response(status_code=204))

        with patch("app.middleware.request_context.reset_context") as mock_rst:
            resp = await request_context_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.headers["X-Request-ID"], "corr-id-1")
        self.assertGreaterEqual(mock_rst.call_count, 1)

    async def test_reset_context_on_inner_error(self):
        req = MagicMock()
        req.headers.get = MagicMock(return_value=None)

        async def boom(_r):
            raise RuntimeError("fail")

        with (
            patch("app.middleware.request_context.reset_context") as mock_rst,
            patch(
                "app.middleware.request_context.resolve_request_uuid",
                return_value="gen-id",
            ),
        ):
            with self.assertRaises(RuntimeError):
                await request_context_middleware(req, boom)

        self.assertGreaterEqual(mock_rst.call_count, 1)
