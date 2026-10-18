# tests/middleware/test_cors_setup.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock, patch

from fastapi.middleware.cors import CORSMiddleware

from app.middleware.cors_setup import cors_setup_middleware


class TestCorsSetupMiddleware(unittest.TestCase):
    def test_configures_cors_middleware_with_expected_options(self):
        app = MagicMock()
        config = MagicMock()
        config.CORS_ALLOW_ORIGINS = (
            "http://localhost:3000, http://localhost:5173, ,"
        )
        config.CORS_MAX_AGE_SECONDS = 86400

        with patch(
            "app.middleware.cors_setup.get_config",
            return_value=config,
        ):
            cors_setup_middleware(app)

        app.add_middleware.assert_called_once_with(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://localhost:5173",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=config.CORS_MAX_AGE_SECONDS,
        )
