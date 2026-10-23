# tests/test_main.py
# SPDX-License-Identifier: Apache-2.0

import importlib
import os
import sys
import unittest
from unittest.mock import patch

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.config import get_config
from app.constants import HIDDEN_TITLE
from app.errors import (
    BadGatewayError,
    InternalServerError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from app.handlers import (
    bad_gateway_handler,
    internal_server_error_handler,
    service_unavailable_handler,
    unauthorized_handler,
)
from app.middleware.request_context import request_context_middleware
from app.middleware.request_logging import request_logging_middleware
from app.middleware.security_headers import security_headers_middleware
from app.version import __version__

_ENV = {
    "INSTALL_SOURCE_CODE": "/opt/hidden",
    "INSTALL_CIPHERDIR": "/cipher",
    "INSTALL_MOUNTPOINT": "/mount",
    "INSTALL_SECRETS": "/secrets",
    "UVICORN_HOST": "127.0.0.1",
    "UVICORN_PORT": "8081",
    "WATCHDOG_INTERVAL_SECONDS": "60",
    "WATCHDOG_LIVENESS_SECONDS": "120",
    "API_PREFIX": "/api/v1",
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "%(message)s",
    "CORS_ALLOW_ORIGINS": "http://localhost:3000, http://localhost:5173, ,",
    "CORS_MAX_AGE_SECONDS": "86400",
    "VERSITY_HOST": "127.0.0.1",
    "VERSITY_PORT": "9000",
    "VERSITY_WEBGUI_HOST": "127.0.0.1",
    "VERSITY_WEBGUI_PORT": "8080",
    "VERSITY_WEBGUI_GATEWAY": "http://localhost:9000",
    "VERSITY_WEBGUI_CORS_ALLOW_ORIGIN": "http://localhost:8080",
    "VERSITY_START_TIMEOUT_SECONDS": "5",
    "VERSITY_STOP_TIMEOUT_SECONDS": "5",
    "VERSITY_POLL_INTERVAL_SECONDS": "0.25",
}

_ROUTES = {
    "/api/v1/gocryptfs/health": {"GET"},
    "/api/v1/gocryptfs/init": {"POST"},
    "/api/v1/gocryptfs/mount": {"POST"},
    "/api/v1/gocryptfs/unmount": {"POST"},
    "/api/v1/gocryptfs/reveal": {"POST"},
    "/api/v1/gocryptfs/rotate": {"POST"},
    "/api/v1/gocryptfs/reset": {"POST"},
}


class TestApplication(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls._env = patch.dict(os.environ, _ENV)
        cls._env.start()
        get_config.cache_clear()
        sys.modules.pop("app.main", None)
        cls.main = importlib.import_module("app.main")

    @classmethod
    def tearDownClass(cls):
        get_config.cache_clear()
        cls._env.stop()

    def test_builds_api(self):
        app = self.main.app

        self.assertEqual(app.title, HIDDEN_TITLE)
        self.assertEqual(app.version, __version__)
        self.assertEqual(
            app.swagger_ui_parameters,
            {
                "persistAuthorization": True,
                "displayRequestDuration": True,
                "tryItOutEnabled": True,
            },
        )
        self.assertEqual(
            self.main.config.GOCRYPTFS_PASSPHRASE_PATH,
            "/secrets/gocryptfs_passphrase.enc",
        )
        routes = {
            route.path: route.methods
            for route in app.routes
            if getattr(route, "path", "").startswith("/api/v1/")
        }
        self.assertEqual(routes, _ROUTES)
        self.assertIs(
            app.exception_handlers[UnauthorizedError],
            unauthorized_handler,
        )
        self.assertIs(
            app.exception_handlers[InternalServerError],
            internal_server_error_handler,
        )
        self.assertIs(
            app.exception_handlers[BadGatewayError],
            bad_gateway_handler,
        )
        self.assertIs(
            app.exception_handlers[ServiceUnavailableError],
            service_unavailable_handler,
        )

        stack = app.user_middleware
        self.assertIs(stack[0].cls, GZipMiddleware)
        self.assertIs(stack[1].cls, CORSMiddleware)
        self.assertEqual(
            stack[1].kwargs["allow_origins"],
            ["http://localhost:3000", "http://localhost:5173"],
        )
        self.assertIs(stack[1].kwargs["allow_credentials"], True)
        self.assertEqual(stack[1].kwargs["allow_methods"], ["*"])
        self.assertEqual(stack[1].kwargs["allow_headers"], ["*"])
        self.assertEqual(stack[1].kwargs["max_age"], 86400)
        self.assertIs(
            stack[2].kwargs["dispatch"],
            security_headers_middleware,
        )
        self.assertIs(
            stack[3].kwargs["dispatch"],
            request_context_middleware,
        )
        self.assertIs(
            stack[4].kwargs["dispatch"],
            request_logging_middleware,
        )

    async def test_lifespan_configures_logging(self):
        with patch("app.main.init_logging") as init_logging:
            async with self.main.lifespan(self.main.app):
                init_logging.assert_called_once_with()
