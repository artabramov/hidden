# tests/security/test_jwt.py
# SPDX-License-Identifier: GPL-3.0-only

import time
import unittest
from unittest.mock import MagicMock, patch

import jwt

from app.security import jwt as jwt_module


class TestJwt(unittest.TestCase):
    def test_generate_jti_returns_hex_string(self):
        value = jwt_module.generate_jti()

        self.assertIsInstance(value, str)
        self.assertEqual(len(value), 32)
        int(value, 16)

    def test_generate_jti_returns_unique_values(self):
        value_1 = jwt_module.generate_jti()
        value_2 = jwt_module.generate_jti()

        self.assertNotEqual(value_1, value_2)

    def test_create_auth_token_builds_expected_payload(self):
        config = MagicMock()
        config.AUTH_TOKEN_TTL_SECONDS = 3600
        config.JWT_SIGNING_KEY = "test-signing-key"

        with (
            patch(
                "app.security.jwt.get_config",
                return_value=config,
            ),
            patch(
                "app.security.jwt.time.time",
                return_value=1_700_000_000,
            ),
        ):
            token = jwt_module.create_auth_token(
                user_id=123,
                current_jti="abc123jti",
            )

        payload = jwt.decode(
            token,
            config.JWT_SIGNING_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )

        self.assertEqual(payload["sub"], "123")
        self.assertEqual(payload["iat"], 1_700_000_000)
        self.assertEqual(payload["jti"], "abc123jti")
        self.assertEqual(payload["exp"], 1_700_003_600)

    def test_create_auth_token_uses_configured_signing_key(self):
        config = MagicMock()
        config.AUTH_TOKEN_TTL_SECONDS = 600
        config.JWT_SIGNING_KEY = "signing-key-1"

        with patch(
            "app.security.jwt.get_config",
            return_value=config,
        ):
            token = jwt_module.create_auth_token(
                user_id=1,
                current_jti="jti-1",
            )

        decoded = jwt.decode(
            token,
            "signing-key-1",
            algorithms=["HS256"],
        )

        self.assertEqual(decoded["sub"], "1")
        self.assertEqual(decoded["jti"], "jti-1")

    def test_decode_auth_token_returns_payload_for_valid_token(self):
        config = MagicMock()
        config.JWT_SIGNING_KEY = "test-signing-key"

        token = jwt.encode(
            {
                "sub": "42",
                "iat": int(time.time()),
                "jti": "valid-jti",
                "exp": int(time.time()) + 3600,
            },
            config.JWT_SIGNING_KEY,
            algorithm="HS256",
        )

        with patch(
            "app.security.jwt.get_config",
            return_value=config,
        ):
            payload = jwt_module.decode_auth_token(token)

        self.assertEqual(payload["sub"], "42")
        self.assertEqual(payload["jti"], "valid-jti")

    def test_decode_auth_token_raises_for_invalid_token(self):
        config = MagicMock()
        config.JWT_SIGNING_KEY = "test-signing-key"

        with patch(
            "app.security.jwt.get_config",
            return_value=config,
        ):
            with self.assertRaises(jwt.InvalidTokenError):
                jwt_module.decode_auth_token("not-a-valid-jwt")

    def test_decode_auth_token_raises_for_wrong_signing_key(self):
        token = jwt.encode(
            {
                "sub": "42",
                "iat": int(time.time()),
                "jti": "valid-jti",
                "exp": int(time.time()) + 3600,
            },
            "correct-signing-key",
            algorithm="HS256",
        )

        config = MagicMock()
        config.JWT_SIGNING_KEY = "wrong-signing-key"

        with patch(
            "app.security.jwt.get_config",
            return_value=config,
        ):
            with self.assertRaises(jwt.InvalidTokenError):
                jwt_module.decode_auth_token(token)

    def test_decode_auth_token_raises_for_expired_token(self):
        config = MagicMock()
        config.JWT_SIGNING_KEY = "test-signing-key"

        token = jwt.encode(
            {
                "sub": "42",
                "iat": 1_700_000_000,
                "jti": "expired-jti",
                "exp": 1,
            },
            config.JWT_SIGNING_KEY,
            algorithm="HS256",
        )

        with patch(
            "app.security.jwt.get_config",
            return_value=config,
        ):
            with self.assertRaises(jwt.ExpiredSignatureError):
                jwt_module.decode_auth_token(token)

    def test_create_auth_token_disable_exp_omits_exp(self):
        config = MagicMock()
        config.JWT_SIGNING_KEY = "test-signing-key"

        with (
            patch(
                "app.security.jwt.get_config",
                return_value=config,
            ),
            patch(
                "app.security.jwt.time.time",
                return_value=1_700_000_000,
            ),
        ):
            token = jwt_module.create_auth_token(
                user_id=7,
                current_jti="perm-jti",
                disable_exp=True,
            )

        payload = jwt.decode(
            token,
            config.JWT_SIGNING_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )

        self.assertEqual(payload["sub"], "7")
        self.assertEqual(payload["jti"], "perm-jti")
        self.assertEqual(payload["iat"], 1_700_000_000)
        self.assertNotIn("exp", payload)

    def test_create_auth_token_stores_sub_as_string(self):
        config = MagicMock()
        config.AUTH_TOKEN_TTL_SECONDS = 300
        config.JWT_SIGNING_KEY = "test-signing-key"

        with patch(
            "app.security.jwt.get_config",
            return_value=config,
        ):
            token = jwt_module.create_auth_token(
                user_id=999,
                current_jti="jti-999",
            )

        payload = jwt.decode(
            token,
            config.JWT_SIGNING_KEY,
            algorithms=["HS256"],
        )

        self.assertEqual(payload["sub"], "999")
        self.assertIsInstance(payload["sub"], str)
