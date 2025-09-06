import unittest
from unittest.mock import patch
from dataclasses import fields
from app.config import get_config, Config


class ConfigTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        get_config.cache_clear()

    def build_env(self, **overrides) -> dict[str, str]:
        env: dict[str, str] = {}
        for f in fields(Config):
            if f.type is str:
                env[f.name] = "value"
            elif f.type is int:
                env[f.name] = "123"
            elif f.type is bool:
                env[f.name] = "true"
            elif f.type is list:
                env[f.name] = "a, b, c"
            elif f.type is bytes:
                env[f.name] = "bytes-value"
        env.update({k: str(v) for k, v in overrides.items()})
        return env

    @patch("app.config.dotenv_values")
    async def test_parses_and_trims(self, dotenv_mock):
        env = self.build_env(
            LOG_NAME="  MyApp  ",
            LOG_FILESIZE="  4096  ",
            REDIS_ENABLED="  TRUE  ",
            CRYPTO_HKDF_INFO="  aesgcm-v1  ",
        )
        dotenv_mock.return_value = env

        cfg = get_config()
        self.assertEqual(cfg.LOG_NAME, "MyApp")
        self.assertEqual(cfg.LOG_FILESIZE, 4096)
        self.assertTrue(cfg.REDIS_ENABLED)
        self.assertEqual(cfg.CRYPTO_HKDF_INFO, b"aesgcm-v1")

        self.assertIsInstance(cfg.LOG_NAME, str)
        self.assertIsInstance(cfg.LOG_FILESIZE, int)
        self.assertIsInstance(cfg.REDIS_ENABLED, bool)
        self.assertIsInstance(cfg.CRYPTO_HKDF_INFO, bytes)

    @patch("app.config.dotenv_values")
    async def test_missing_key_raises_keyerror(self, dotenv_mock):
        env = self.build_env()
        env.pop("SECRET_KEY_PATH", None)
        dotenv_mock.return_value = env

        with self.assertRaises(KeyError):
            get_config()

    @patch("app.config.dotenv_values")
    async def test_invalid_int_raises_valueerror(self, dotenv_mock):
        env = self.build_env(LOG_FILESIZE="not-an-int")
        dotenv_mock.return_value = env

        with self.assertRaises(ValueError):
            get_config()

    @patch("app.config.dotenv_values")
    async def test_invalid_bool_raises_keyerror(self, dotenv_mock):
        env = self.build_env(REDIS_ENABLED="yes")
        dotenv_mock.return_value = env

        with self.assertRaises(KeyError):
            get_config()

    @patch("app.config.dotenv_values")
    async def test_lru_cache_memoizes(self, dotenv_mock):
        env1 = self.build_env(LOG_LEVEL="info")
        dotenv_mock.return_value = env1
        cfg1 = get_config()
        self.assertEqual(cfg1.LOG_LEVEL, "info")

        env2 = self.build_env(LOG_LEVEL="debug")
        dotenv_mock.return_value = env2
        cfg2 = get_config()
        self.assertIs(cfg1, cfg2)
        self.assertEqual(cfg2.LOG_LEVEL, "info")

        get_config.cache_clear()
        cfg3 = get_config()
        self.assertEqual(cfg3.LOG_LEVEL, "debug")

    @patch("app.config.dotenv_values")
    async def test_bytes_and_none_mapping(self, dotenv_mock):
        env = self.build_env(
            CRYPTO_HKDF_INFO="  aesgcm-v1  ",
            CRYPTO_AAD_DEFAULT="None",
            LOG_FILENAME="None",
        )
        dotenv_mock.return_value = env

        cfg = get_config()
        self.assertEqual(cfg.CRYPTO_HKDF_INFO, b"aesgcm-v1")
        self.assertIsNone(cfg.CRYPTO_AAD_DEFAULT)
        self.assertIsNone(cfg.LOG_FILENAME)

    @patch("app.config.dotenv_values")
    async def test_list_parsing_and_none(self, dotenv_mock):
        env = self.build_env(
            JWT_ALGORITHMS="",
        )
        dotenv_mock.return_value = env
        cfg_empty = get_config()
        self.assertEqual(cfg_empty.JWT_ALGORITHMS, [])

        get_config.cache_clear()
        env = self.build_env(
            JWT_ALGORITHMS="None",
        )
        dotenv_mock.return_value = env
        cfg_none = get_config()
        self.assertIsNone(cfg_none.JWT_ALGORITHMS)
