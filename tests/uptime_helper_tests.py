import unittest
from unittest.mock import patch
from app.helpers.uptime_helper import Uptime


class UptimeHelperTestCase(unittest.TestCase):

    @patch("time.time", return_value=1000.0)
    def test_uptime_initialization(self, mock_time):
        uptime = Uptime()
        self.assertEqual(uptime.started_time, 1000.0)

    @patch("time.time", side_effect=[1000.0, 1005.0])
    def test_get_uptime(self, mock_time):
        uptime = Uptime()
        result = uptime.get_uptime()
        self.assertEqual(result, 5)

    @patch("time.time", side_effect=[1000.0, 1000.5])
    def test_get_uptime_small_time_diff(self, mock_time):
        uptime = Uptime()
        result = uptime.get_uptime()
        self.assertEqual(result, 0)

    @patch("time.time", side_effect=[1000.0, 1020.0])
    def test_get_uptime_large_time_diff(self, mock_time):
        uptime = Uptime()
        result = uptime.get_uptime()
        self.assertEqual(result, 20)


if __name__ == "__main__":
    unittest.main()
