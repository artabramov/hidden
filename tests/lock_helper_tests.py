import unittest
from unittest.mock import patch, AsyncMock
from app.helpers.lock_helper import (
    lock_exists, lock_enable, lock_disable)
from app.config import get_config

cfg = get_config()


class LockHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.lock_helper.FileManager")
    async def test_lock_exists_true(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = True

        FileManagerMock.file_exists = file_exists_mock
        result = await lock_exists()

        self.assertTrue(result)
        file_exists_mock.assert_called_with(cfg.APP_LOCK_PATH)

    @patch("app.helpers.lock_helper.FileManager")
    async def test_lock_exists_false(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = False

        FileManagerMock.file_exists = file_exists_mock
        result = await lock_exists()

        self.assertFalse(result)
        file_exists_mock.assert_called_with(cfg.APP_LOCK_PATH)

    @patch("app.helpers.lock_helper.FileManager", new_callable=AsyncMock)
    async def test_lock_enable_not_locked(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = False
        FileManagerMock.file_exists = file_exists_mock
        await lock_enable()

        file_exists_mock.assert_called_once()
        FileManagerMock.write.assert_called_once_with(
            cfg.APP_LOCK_PATH, bytes())

    @patch("app.helpers.lock_helper.FileManager", new_callable=AsyncMock)
    async def test_lock_enable_locked(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = True
        FileManagerMock.file_exists = file_exists_mock
        await lock_enable()

        file_exists_mock.assert_called_once()
        FileManagerMock.write.assert_not_called()

    @patch("app.helpers.lock_helper.FileManager", new_callable=AsyncMock)
    async def test_lock_disable_not_locked(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = False
        FileManagerMock.file_exists = file_exists_mock
        await lock_disable()

        file_exists_mock.assert_called_once()
        FileManagerMock.delete.assert_not_called()

    @patch("app.helpers.lock_helper.FileManager", new_callable=AsyncMock)
    async def test_lock_disable_locked(self, FileManagerMock):
        file_exists_mock = AsyncMock()
        file_exists_mock.return_value = True
        FileManagerMock.file_exists = file_exists_mock
        await lock_disable()

        file_exists_mock.assert_called_once()
        FileManagerMock.delete.assert_called_once_with(cfg.APP_LOCK_PATH)


if __name__ == "__main__":
    unittest.main()
