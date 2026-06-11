# tests/middleware/test_lockdown_mode.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from starlette.responses import Response

from app.middleware.lockdown_mode import lockdown_mode_middleware


def _request(path: str) -> MagicMock:
    req = MagicMock()
    req.url.path = path
    return req


class TestLockdownModeMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_flag_absent_passes_through(self):
        req = _request("/api/v1/x")
        inner = AsyncMock(return_value=Response(status_code=200))

        with (
            patch(
                "app.middleware.lockdown_mode.isfile",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.middleware.lockdown_mode.get_config",
                return_value=MagicMock(API_PREFIX="/api/v1"),
            ),
        ):
            resp = await lockdown_mode_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.status_code, 200)

    async def test_flag_present_init_prefix_passes(self):
        req = _request("/api/v1/init/state")
        inner = AsyncMock(return_value=Response(status_code=200))

        with (
            patch(
                "app.middleware.lockdown_mode.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.middleware.lockdown_mode.get_config",
                return_value=MagicMock(API_PREFIX="/api/v1"),
            ),
        ):
            resp = await lockdown_mode_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.status_code, 200)

    async def test_flag_present_excluded_docs_passes(self):
        req = _request("/docs")
        inner = AsyncMock(return_value=Response(status_code=200))

        with (
            patch(
                "app.middleware.lockdown_mode.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.middleware.lockdown_mode.get_config",
                return_value=MagicMock(API_PREFIX="/api/v1"),
            ),
        ):
            resp = await lockdown_mode_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.status_code, 200)

    async def test_flag_present_blocks_other_paths(self):
        req = _request("/api/v1/users")
        inner = AsyncMock()

        with (
            patch(
                "app.middleware.lockdown_mode.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.middleware.lockdown_mode.get_config",
                return_value=MagicMock(API_PREFIX="/api/v1"),
            ),
        ):
            resp = await lockdown_mode_middleware(req, inner)

        inner.assert_not_awaited()
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(resp.headers.get("Retry-After"), "300")
