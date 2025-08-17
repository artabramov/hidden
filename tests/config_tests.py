import unittest
from app.config import get_config


class ConfigTest(unittest.IsolatedAsyncioTestCase):

    async def test_config(self):
        get_config.cache_clear()
        cfg = get_config()
        self.assertEqual(len(cfg.__dict__), 62)

        self.assertTrue(isinstance(cfg.SECRET_KEY_PATH, str))

        self.assertTrue(isinstance(cfg.CRYPTOGRAPHY_SALT_LENGTH, int))
        self.assertTrue(isinstance(cfg.CRYPTOGRAPHY_KEY_LENGTH, int))
        self.assertTrue(isinstance(cfg.CRYPTOGRAPHY_IV_LENGTH, int))
        self.assertTrue(isinstance(cfg.CRYPTOGRAPHY_PBKDF2_ITERATIONS, int))

        self.assertTrue(isinstance(cfg.LOG_LEVEL, str))
        self.assertTrue(isinstance(cfg.LOG_NAME, str))
        self.assertTrue(isinstance(cfg.LOG_FORMAT, str))
        self.assertTrue(isinstance(cfg.LOG_FILENAME, str))
        self.assertTrue(isinstance(cfg.LOG_FILESIZE, int))
        self.assertTrue(isinstance(cfg.LOG_FILES_LIMIT, int))

        self.assertTrue(isinstance(cfg.UVICORN_HOST, str))
        self.assertTrue(isinstance(cfg.UVICORN_PORT, int))
        self.assertTrue(isinstance(cfg.UVICORN_WORKERS, int))

        self.assertTrue(isinstance(cfg.POSTGRES_HOST, str))
        self.assertTrue(isinstance(cfg.POSTGRES_PORT, int))
        self.assertTrue(isinstance(cfg.POSTGRES_DATABASE, str))
        self.assertTrue(isinstance(cfg.POSTGRES_USERNAME, str))
        self.assertTrue(isinstance(cfg.POSTGRES_PASSWORD, str))
        self.assertTrue(isinstance(cfg.POSTGRES_POOL_SIZE, int))
        self.assertTrue(isinstance(cfg.POSTGRES_POOL_OVERFLOW, int))

        self.assertTrue(isinstance(cfg.REDIS_ENABLED, bool))
        self.assertTrue(isinstance(cfg.REDIS_HOST, str))
        self.assertTrue(isinstance(cfg.REDIS_PORT, int))
        self.assertTrue(isinstance(cfg.REDIS_DECODE_RESPONSES, bool))
        self.assertTrue(isinstance(cfg.REDIS_EXPIRE, int))

        self.assertTrue(isinstance(cfg.SPHINX_PATH, str))
        self.assertTrue(isinstance(cfg.SPHINX_NAME, str))
        self.assertTrue(isinstance(cfg.SPHINX_URL, str))

        self.assertTrue(isinstance(cfg.JTI_LENGTH, int))
        self.assertTrue(isinstance(cfg.JWT_EXPIRES, int))
        self.assertTrue(isinstance(cfg.JWT_ALGORITHM, str))
        self.assertTrue(isinstance(cfg.JWT_SECRET, str))

        self.assertTrue(isinstance(cfg.ADDONS_ENABLED, list))
        self.assertTrue(isinstance(cfg.ADDONS_PATH, str))

        self.assertTrue(isinstance(cfg.APP_API_VERSION, str))
        self.assertTrue(isinstance(cfg.APP_URL, str))
        self.assertTrue(isinstance(cfg.APP_SHRED_CYCLES, int))
        self.assertTrue(isinstance(cfg.APP_SHUFFLE_LIMIT, int))
        self.assertTrue(isinstance(cfg.APP_LOCK_PATH, str))

        self.assertTrue(isinstance(cfg.HTML_PATH, str))
        self.assertTrue(isinstance(cfg.HTML_FILE, str))

        self.assertTrue(isinstance(cfg.USER_PASSWORD_ATTEMPTS, int))
        self.assertTrue(isinstance(cfg.USER_TOTP_ATTEMPTS, int))
        self.assertTrue(isinstance(cfg.USER_SUSPENDED_TIME, int))

        self.assertTrue(isinstance(cfg.USERPICS_PATH, str))
        self.assertTrue(isinstance(cfg.USERPICS_URL, str))
        self.assertTrue(isinstance(cfg.USERPICS_PREFIX, str))
        self.assertTrue(isinstance(cfg.USERPICS_WIDTH, int))
        self.assertTrue(isinstance(cfg.USERPICS_HEIGHT, int))
        self.assertTrue(isinstance(cfg.USERPICS_QUALITY, int))
        self.assertTrue(isinstance(cfg.USERPICS_LRU_SIZE, int))

        self.assertTrue(isinstance(cfg.THUMBNAILS_PATH, str))
        self.assertTrue(isinstance(cfg.THUMBNAILS_URL, str))
        self.assertTrue(isinstance(cfg.THUMBNAILS_PREFIX, str))
        self.assertTrue(isinstance(cfg.THUMBNAILS_WIDTH, int))
        self.assertTrue(isinstance(cfg.THUMBNAILS_HEIGHT, int))
        self.assertTrue(isinstance(cfg.THUMBNAILS_QUALITY, int))
        self.assertTrue(isinstance(cfg.THUMBNAILS_LRU_SIZE, int))

        self.assertTrue(isinstance(cfg.DOCUMENTS_PATH, str))
        self.assertTrue(isinstance(cfg.DOCUMENTS_URL, str))
        self.assertTrue(isinstance(cfg.DOCUMENTS_LRU_SIZE, int))


if __name__ == "__main__":
    unittest.main()
