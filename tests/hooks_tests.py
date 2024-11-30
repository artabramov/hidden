import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.hooks import Hook


class HookTestCase(unittest.TestCase):

    @patch("app.hooks.get_context")
    @patch("app.hooks.AsyncSession")
    @patch("app.hooks.Redis")
    def setUp(self, MockRedis, MockSession, mock_get_context):
        """Set up the test case environment."""
        # Mock session and cache
        self.mock_session = MockSession()
        self.mock_cache = MockRedis()

        # Mock the context (ctx.hooks)
        self.mock_ctx = MagicMock()
        self.mock_hooks = {
            'test_hook': [AsyncMock(), AsyncMock()]
        }
        self.mock_ctx.hooks = self.mock_hooks
        mock_get_context.return_value = self.mock_ctx

        # Initialize the Hook object
        self.hook = Hook(self.mock_session, self.mock_cache)

    @patch("app.hooks.get_context")
    @patch("app.hooks.AsyncSession")
    @patch("app.hooks.Redis")
    async def test_do_executes_hooks(self, MockRedis, MockSession,
                                     mock_get_context):
        """Test that the do method executes the correct hook functions."""
        # Setup
        hook_name = 'test_hook'
        arg1 = 'arg1'
        arg2 = 'arg2'

        # The mock functions we expect to be called
        hook_func1 = self.mock_hooks[hook_name][0]
        hook_func2 = self.mock_hooks[hook_name][1]

        # Call the `do` method
        await self.hook.do(hook_name, arg1, arg2)

        # Check if the functions are called in order
        hook_func1.assert_awaited_with(
            self.mock_session, self.mock_cache, None, arg1, arg2)
        hook_func2.assert_awaited_with(
            self.mock_session, self.mock_cache, None, arg1, arg2)

    @patch("app.hooks.get_context")
    @patch("app.hooks.AsyncSession")
    @patch("app.hooks.Redis")
    async def test_do_does_not_call_hooks_if_not_found(
            self, MockRedis, MockSession, mock_get_context):
        """
        Test that the do method does not call any hook functions if hook
        is not found.
        """
        # Setup
        hook_name = 'non_existing_hook'
        arg1 = 'arg1'
        arg2 = 'arg2'

        # Call the `do` method with a non-existing hook
        await self.hook.do(hook_name, arg1, arg2)

        # Ensure that no hooks were called
        self.mock_ctx.hooks.get.assert_called_once_with(hook_name)
        self.assertEqual(len(self.mock_hooks.get(hook_name, [])), 0)

    @patch("app.hooks.get_context")
    @patch("app.hooks.AsyncSession")
    @patch("app.hooks.Redis")
    async def test_do_with_current_user(self, MockRedis, MockSession,
                                        mock_get_context):
        """
        Test that the do method uses the current_user when executing
        hooks.
        """
        # Setup
        hook_name = 'test_hook'
        arg1 = 'arg1'
        arg2 = 'arg2'
        current_user = MagicMock()
        self.hook.current_user = current_user

        # The mock functions we expect to be called
        hook_func1 = self.mock_hooks[hook_name][0]

        # Call the `do` method
        await self.hook.do(hook_name, arg1, arg2)

        # Check that the hook function uses the current user
        hook_func1.assert_awaited_with(self.mock_session, self.mock_cache,
                                       current_user, arg1, arg2)

    @patch("app.hooks.get_context")
    @patch("app.hooks.AsyncSession")
    @patch("app.hooks.Redis")
    async def test_do_logs_error_if_exception_in_hook(
            self, MockRedis, MockSession, mock_get_context):
        """
        Test that the do method handles errors in hooks gracefully and
        logs the error.
        """

        # Setup
        hook_name = 'test_hook'
        arg1 = 'arg1'
        arg2 = 'arg2'

        # Mock the hook function to raise an exception
        hook_func1 = self.mock_hooks[hook_name][0]
        hook_func1.side_effect = Exception("Test Exception")

        # Call the `do` method and assert it logs the error
        with self.assertRaises(Exception):
            await self.hook.do(hook_name, arg1, arg2)

        # Ensure the exception was logged
        mock_get_context.return_value.log.debug.assert_called_with(
            "Hook error; filename=test_hook; e=Test Exception;"
        )


if __name__ == "__main__":
    unittest.main()
