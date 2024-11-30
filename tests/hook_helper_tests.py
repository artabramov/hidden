import unittest
from unittest.mock import patch, MagicMock
from app.helpers.hook_helper import load_hooks


class HooHelperTestCase(unittest.TestCase):

    @patch("app.helpers.hook_helper.importlib.util.spec_from_file_location")
    @patch("app.helpers.hook_helper.importlib.util.module_from_spec")
    @patch("app.helpers.hook_helper.get_context")
    @patch("app.helpers.hook_helper.get_log")
    async def test__load_hooks_success(self, mock_get_log, mock_get_context,
                                       mock_module_from_spec,
                                       mock_spec_from_file_location):
        """Test successful loading of hooks from plugins."""

        # Mock configuration and context
        mock_cfg = MagicMock()
        mock_cfg.PLUGINS_ENABLED = ["plugin1", "plugin2"]
        mock_cfg.PLUGINS_BASE_PATH = "/path/to/plugins"

        # Mock context and log
        mock_ctx = MagicMock()
        mock_get_context.return_value = mock_ctx
        mock_log = MagicMock()
        mock_get_log.return_value = mock_log

        # Mock modules to simulate plugins
        mock_spec = MagicMock()
        mock_spec_from_file_location.return_value = mock_spec

        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        # Mock functions in plugin modules
        def mock_func_1():
            pass

        def mock_func_2():
            pass

        mock_module.__dict__ = {
            "func_1": mock_func_1,
            "func_2": mock_func_2
        }

        # Run load_hooks
        await load_hooks()

        # Check that the correct functions were registered
        self.assertIn("func_1", mock_ctx.hooks)
        self.assertIn("func_2", mock_ctx.hooks)
        self.assertEqual(len(mock_ctx.hooks["func_1"]), 1)
        self.assertEqual(len(mock_ctx.hooks["func_2"]), 1)

    @patch("app.helpers.hook_helper.importlib.util.spec_from_file_location")
    @patch("app.helpers.hook_helper.importlib.util.module_from_spec")
    @patch("app.helpers.hook_helper.get_context")
    @patch("app.helpers.hook_helper.get_log")
    async def test__load_hooks_error_loading_module(
            self, mock_get_log, mock_get_context, mock_module_from_spec,
            mock_spec_from_file_location):
        """Test that error loading a plugin module is handled."""

        # Mock configuration and context
        mock_cfg = MagicMock()
        mock_cfg.PLUGINS_ENABLED = ["plugin1"]
        mock_cfg.PLUGINS_BASE_PATH = "/path/to/plugins"

        # Mock context and log
        mock_ctx = MagicMock()
        mock_get_context.return_value = mock_ctx
        mock_log = MagicMock()
        mock_get_log.return_value = mock_log

        # Mock the module load to raise an error
        mock_spec = MagicMock()
        mock_spec_from_file_location.return_value = mock_spec

        mock_module_from_spec.side_effect = Exception("Module loading error")

        # Run load_hooks and ensure exception is raised
        with self.assertRaises(Exception):
            await load_hooks()

        # Check if the error was logged
        mock_log.debug.assert_called_with(
            "Hook error; filename=plugin1.py; e=Module loading error;")

    @patch("app.helpers.hook_helper.importlib.util.spec_from_file_location")
    @patch("app.helpers.hook_helper.importlib.util.module_from_spec")
    @patch("app.helpers.hook_helper.get_context")
    @patch("app.helpers.hook_helper.get_log")
    async def test__load_hooks_function_override(
            self, mock_get_log, mock_get_context, mock_module_from_spec,
            mock_spec_from_file_location):
        """
        Test that functions with the same name from different plugins
        are correctly added to hooks.
        """

        # Mock configuration and context
        mock_cfg = MagicMock()
        mock_cfg.PLUGINS_ENABLED = ["plugin1", "plugin2"]
        mock_cfg.PLUGINS_BASE_PATH = "/path/to/plugins"

        # Mock context and log
        mock_ctx = MagicMock()
        mock_get_context.return_value = mock_ctx
        mock_log = MagicMock()
        mock_get_log.return_value = mock_log

        # Mock modules to simulate plugins
        mock_spec = MagicMock()
        mock_spec_from_file_location.return_value = mock_spec

        # Mock functions in plugin modules
        def mock_func_1():
            pass

        def mock_func_2():
            pass

        def mock_func_1_plugin2():
            pass

        mock_module_1 = MagicMock()
        mock_module_1.__dict__ = {
            "func_1": mock_func_1
        }

        mock_module_2 = MagicMock()
        mock_module_2.__dict__ = {
            "func_1": mock_func_1_plugin2,
            "func_2": mock_func_2
        }

        # Mock module loading to return different modules
        mock_module_from_spec.side_effect = [mock_module_1, mock_module_2]

        # Run load_hooks
        await load_hooks()

        # Check that both versions of func_1 were added to hooks
        self.assertEqual(len(mock_ctx.hooks["func_1"]), 2)
        self.assertIn("func_2", mock_ctx.hooks)

    @patch("app.helpers.hook_helper.importlib.util.spec_from_file_location")
    @patch("app.helpers.hook_helper.importlib.util.module_from_spec")
    @patch("app.helpers.hook_helper.get_context")
    @patch("app.helpers.hook_helper.get_log")
    async def test__load_hooks_file_not_found(
            self, mock_get_log, mock_get_context, mock_module_from_spec,
            mock_spec_from_file_location):
        """Test that a file not found error is handled."""

        # Mock configuration and context
        mock_cfg = MagicMock()
        mock_cfg.PLUGINS_ENABLED = ["plugin1"]
        mock_cfg.PLUGINS_BASE_PATH = "/path/to/plugins"

        # Mock context and log
        mock_ctx = MagicMock()
        mock_get_context.return_value = mock_ctx
        mock_log = MagicMock()
        mock_get_log.return_value = mock_log

        # Simulate a file not found error
        mock_spec_from_file_location.side_effect = FileNotFoundError(
            "Plugin file not found")

        # Run load_hooks and ensure exception is raised
        with self.assertRaises(FileNotFoundError):
            await load_hooks()

        # Check if the error was logged
        mock_log.debug.assert_called_with(
            "Hook error; filename=plugin1.py; e=Plugin file not found;")


if __name__ == "__main__":
    unittest.main()
