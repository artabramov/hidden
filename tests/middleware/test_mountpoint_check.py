# tests/middleware/test_mountpoint_check.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from starlette.responses import Response

from app.middleware.mountpoint_check import mountpoint_check_middleware


def _request(path: str) -> MagicMock:
    req = MagicMock()
    req.url.path = path
    return req


def _config() -> MagicMock:
    cfg = MagicMock()
    cfg.API_PREFIX = "/api/v1"
    cfg.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH = "/sec/pass.enc"
    cfg.GOCRYPTFS_MOUNTPOINT = "/mnt/hidden"
    return cfg


class TestMountpointCheckMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_init_prefix_skips_checks(self):
        req = _request("/api/v1/init/x")
        inner = AsyncMock(return_value=Response(status_code=200))

        with patch(
            "app.middleware.mountpoint_check.get_config",
            return_value=_config(),
        ):
            resp = await mountpoint_check_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.status_code, 200)

    async def test_openapi_excluded_skips_checks(self):
        req = _request("/openapi.json")
        inner = AsyncMock(return_value=Response(status_code=200))

        with patch(
            "app.middleware.mountpoint_check.get_config",
            return_value=_config(),
        ):
            resp = await mountpoint_check_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.status_code, 200)

    async def test_passphrase_missing_returns_503(self):
        req = _request("/api/v1/users")
        inner = AsyncMock()

        with (
            patch(
                "app.middleware.mountpoint_check.get_config",
                return_value=_config(),
            ),
            patch(
                "app.middleware.mountpoint_check.isfile",
                new_callable=AsyncMock,
                return_value=False,
            ),
        ):
            resp = await mountpoint_check_middleware(req, inner)

        inner.assert_not_awaited()
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(resp.headers.get("Retry-After"), "300")

    async def test_mountpoint_not_mounted_returns_503(self):
        req = _request("/api/v1/users")
        inner = AsyncMock()

        with (
            patch(
                "app.middleware.mountpoint_check.get_config",
                return_value=_config(),
            ),
            patch(
                "app.middleware.mountpoint_check.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.middleware.mountpoint_check.ismount",
                new_callable=AsyncMock,
                return_value=False,
            ),
        ):
            resp = await mountpoint_check_middleware(req, inner)

        inner.assert_not_awaited()
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    async def test_ready_passes_through(self):
        req = _request("/api/v1/users")
        inner = AsyncMock(return_value=Response(status_code=200))

        with (
            patch(
                "app.middleware.mountpoint_check.get_config",
                return_value=_config(),
            ),
            patch(
                "app.middleware.mountpoint_check.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.middleware.mountpoint_check.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
        ):
            resp = await mountpoint_check_middleware(req, inner)

        inner.assert_awaited_once_with(req)
        self.assertEqual(resp.status_code, 200)
