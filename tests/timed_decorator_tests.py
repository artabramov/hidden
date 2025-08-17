import unittest
from unittest.mock import patch
from app.decorators.timed_decorator import timed


class TimedDecoratorTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.decorators.timed_decorator.log")
    async def test_timed_success(self, log_mock):
        @timed
        async def decorated_function():
            return 123

        result = await decorated_function()
        self.assertEqual(result, 123)

        log_mock.debug.assert_called_once()
        log_mock.error.assert_not_called()

    @patch("app.decorators.timed_decorator.log")
    async def test_timed_error(self, log_mock):
        @timed
        async def decorated_function():
            raise Exception

        with self.assertRaises(Exception):
            await decorated_function()

        log_mock.debug.assert_not_called()
        log_mock.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
