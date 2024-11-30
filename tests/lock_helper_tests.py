import unittest
from unittest.mock import patch
from app.helpers.lock_helper import (
    is_locked, locked_date, lock_enable, lock_disable)
from app.config import get_config

cfg = get_config()


class LockHelperTestCase(unittest.TestCase):

    @patch("app.helpers.lock_helper.os.path.isfile")
    def test__is_locked_true(self, mock_isfile):
        """Test that is_locked returns True when the lock file exists."""
        mock_isfile.return_value = True
        result = is_locked()
        self.assertTrue(result)

    @patch("app.helpers.lock_helper.os.path.isfile")
    def test__is_locked_false(self, mock_isfile):
        """
        Test that is_locked returns False when the lock file does not
        exist.
        """
        mock_isfile.return_value = False
        result = is_locked()
        self.assertFalse(result)

    @patch("app.helpers.lock_helper.os.path.getctime")
    @patch("app.helpers.lock_helper.is_locked")
    def test__locked_date(self, mock_is_locked, mock_getctime):
        """
        Test that locked_date returns the creation time when locked,
        or 0 when not."""
        mock_is_locked.return_value = True
        mock_getctime.return_value = 1234567890
        result = locked_date()
        self.assertEqual(result, 1234567890)

        mock_is_locked.return_value = False
        result = locked_date()
        self.assertEqual(result, 0)

    @patch("app.helpers.lock_helper.FileManager.write")
    @patch("app.helpers.lock_helper.is_locked")
    async def test__lock_enable_create_lock(self, mock_is_locked, mock_write):
        """
        Test that lock_enable creates the lock file if it is not already
        locked.
        """
        mock_is_locked.return_value = False

        await lock_enable()

        mock_write.assert_called_once_with(cfg.APP_LOCK_PATH, bytes())

    @patch("app.helpers.lock_helper.FileManager.write")
    @patch("app.helpers.lock_helper.is_locked")
    async def test__lock_enable_no_create_when_locked(self, mock_is_locked,
                                                      mock_write):
        """
        Test that lock_enable does nothing if the system is already
        locked.
        """
        mock_is_locked.return_value = True

        await lock_enable()
        mock_write.assert_not_called()

    @patch("app.helpers.lock_helper.FileManager.delete")
    @patch("app.helpers.lock_helper.is_locked")
    async def test__lock_disable_remove_lock(self, mock_is_locked,
                                             mock_delete):
        """Test that lock_disable removes the lock file if it exists."""
        mock_is_locked.return_value = True

        await lock_disable()

        mock_delete.assert_called_once_with(cfg.APP_LOCK_PATH)

    @patch("app.helpers.lock_helper.FileManager.delete")
    @patch("app.helpers.lock_helper.is_locked")
    async def test__lock_disable_no_remove_when_not_locked(
            self, mock_is_locked, mock_delete):
        """Test that lock_disable does nothing if the system is not locked."""
        mock_is_locked.return_value = False

        await lock_disable()
        mock_delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()
