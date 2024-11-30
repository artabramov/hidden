import unittest
from unittest.mock import patch
from app.helpers.uptime_helper import Uptime


class UptimeHelperTestCase(unittest.TestCase):

    @patch("time.time", return_value=1000.0)
    def test_uptime_initialization(self, mock_time):
        """
        Test that the Uptime class initializes correctly and records
        start time.
        """
        uptime = Uptime()
        self.assertEqual(uptime.started_time, 1000.0)

    @patch("time.time", side_effect=[1000.0, 1005.0])
    def test_get_uptime(self, mock_time):
        """Test that get_uptime returns the correct uptime in seconds."""
        uptime = Uptime()
        result = uptime.get_uptime()
        self.assertEqual(result, 5)

    @patch("time.time", side_effect=[1000.0, 1000.5])
    def test_get_uptime_small_time_diff(self, mock_time):
        """Test that get_uptime works with small time differences."""
        uptime = Uptime()
        result = uptime.get_uptime()
        self.assertEqual(result, 0)

    @patch("time.time", side_effect=[1000.0, 1020.0])
    def test_get_uptime_large_time_diff(self, mock_time):
        """Test that get_uptime works with larger time differences."""
        uptime = Uptime()
        result = uptime.get_uptime()
        # The difference is 20 seconds
        self.assertEqual(result, 20)


if __name__ == "__main__":
    unittest.main()
