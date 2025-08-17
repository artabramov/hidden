import unittest
from unittest.mock import patch, AsyncMock
from app.helpers.secret_helper import secret_exists, secret_read
from app.config import get_config

cfg = get_config()


class SecretHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.secret_helper.FileManager")
    async def test_secret_exists_true(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = True

        FileManagerMock.file_exists = file_exists_mock
        result = await secret_exists()

        self.assertTrue(result)
        file_exists_mock.assert_called_with(cfg.SECRET_KEY_PATH)

    @patch("app.helpers.secret_helper.FileManager")
    async def test_secret_exists_false(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = False

        FileManagerMock.file_exists = file_exists_mock
        result = await secret_exists()

        self.assertFalse(result)
        file_exists_mock.assert_called_with(cfg.SECRET_KEY_PATH)

    @patch("app.helpers.secret_helper.FileManager")
    async def test_secret_read(self, FileManagerMock):
        read_mock = AsyncMock()
        read_mock.return_value = "secret".encode()

        FileManagerMock.read = read_mock
        result = await secret_read()

        self.assertEqual(result, "secret")
        read_mock.assert_called_with(cfg.SECRET_KEY_PATH)


if __name__ == "__main__":
    unittest.main()
