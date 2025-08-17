import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from types import SimpleNamespace
from app.hook import Hook, init_hooks


class HookTest(unittest.IsolatedAsyncioTestCase):

    def _make_app(self):
        app = MagicMock()
        app.state = SimpleNamespace()
        app.state.hooks = {}
        return app

    def test_init(self):
        app = self._make_app()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        hook = Hook(app, session_mock, cache_mock, current_user_mock)

        self.assertIs(hook.hooks, app.state.hooks)
        self.assertEqual(hook.session, session_mock)
        self.assertEqual(hook.cache, cache_mock)
        self.assertEqual(hook.current_user, current_user_mock)

    async def test_call(self):
        app = self._make_app()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        func1_mock = AsyncMock()
        func2_mock = AsyncMock()
        func3_mock = AsyncMock()

        app.state.hooks = {
            "func1_name": [func1_mock, func2_mock],
            "func2_name": [func3_mock],
        }

        hook = Hook(app, session_mock, cache_mock, current_user_mock)
        await hook.call("func1_name", key="value")

        func1_mock.assert_awaited_with(
            session_mock, cache_mock, current_user_mock, key="value"
        )
        func2_mock.assert_awaited_with(
            session_mock, cache_mock, current_user_mock, key="value"
        )
        func3_mock.assert_not_awaited()

    @patch("app.hook.dir")
    @patch("app.hook.inspect")
    @patch("app.hook.importlib.util.module_from_spec")
    @patch("app.hook.importlib.util.spec_from_file_location")
    @patch("app.hook.cfg")
    async def test_init_hooks(self, cfg_mock, spec_from_file_mock,
                              module_from_spec_mock, inspect_mock,
                              dir_mock):
        cfg_mock.ADDONS_ENABLED = ["addon1", "addon2"]
        cfg_mock.ADDONS_PATH = "/addons"

        spec1_mock = MagicMock()
        spec1_mock.loader = MagicMock()
        spec2_mock = MagicMock()
        spec2_mock.loader = MagicMock()
        spec_from_file_mock.side_effect = [spec1_mock, spec2_mock]

        module1_mock = MagicMock()
        module2_mock = MagicMock()
        module_from_spec_mock.side_effect = [module1_mock, module2_mock]

        inspect_mock.isfunction.return_value = True
        dir_mock.side_effect = [["func1", "func2"], ["func3", "func4"]]

        app = self._make_app()
        await init_hooks(app)

        self.assertListEqual(spec_from_file_mock.call_args_list, [
            call("addon1", "/addons/addon1.py"),
            call("addon2", "/addons/addon2.py"),
        ])
        self.assertListEqual(module_from_spec_mock.call_args_list, [
            call(spec1_mock),
            call(spec2_mock),
        ])
        spec1_mock.loader.exec_module.assert_called_with(module1_mock)
        spec2_mock.loader.exec_module.assert_called_with(module2_mock)

        self.assertIn("func1", app.state.hooks)
        self.assertIn("func2", app.state.hooks)
        self.assertIn("func3", app.state.hooks)
        self.assertIn("func4", app.state.hooks)

        self.assertEqual(len(app.state.hooks["func1"]), 1)
        self.assertEqual(len(app.state.hooks["func2"]), 1)
        self.assertEqual(len(app.state.hooks["func3"]), 1)
        self.assertEqual(len(app.state.hooks["func4"]), 1)


if __name__ == "__main__":
    unittest.main()
