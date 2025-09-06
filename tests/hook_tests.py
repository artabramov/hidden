import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from types import SimpleNamespace
from app.hook import (
    Hook, init_hooks, HOOK_AFTER_USER_REGISTER, HOOK_AFTER_USER_SELECT)


class HookTest(unittest.IsolatedAsyncioTestCase):

    def _make_app(self):
        app = MagicMock()
        app.state = SimpleNamespace()
        app.state.hooks = {}
        return app

    def _make_request(self):
        app = self._make_app()
        return SimpleNamespace(app=app)

    def test_init(self):
        request = self._make_request()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        hook = Hook(request, session_mock, cache_mock, current_user_mock)

        self.assertIs(hook.request, request)
        self.assertEqual(hook.session, session_mock)
        self.assertEqual(hook.cache, cache_mock)
        self.assertEqual(hook.current_user, current_user_mock)

    async def test_call(self):
        request = self._make_request()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        func1_mock = AsyncMock()
        func2_mock = AsyncMock()
        func3_mock = AsyncMock()

        request.app.state.hooks = {
            "func1_name": [func1_mock, func2_mock],
            "func2_name": [func3_mock],
        }

        hook = Hook(request, session_mock, cache_mock, current_user_mock)
        await hook.call("func1_name", key="value")

        func1_mock.assert_awaited_with(
            request, session_mock, cache_mock, current_user_mock, key="value"
        )
        func2_mock.assert_awaited_with(
            request, session_mock, cache_mock, current_user_mock, key="value"
        )
        func3_mock.assert_not_awaited()

    @patch("app.hook.importlib.util.module_from_spec")
    @patch("app.hook.importlib.util.spec_from_file_location")
    async def test_init_hooks(self, spec_from_file_mock,
                              module_from_spec_mock):
        async def a_reg(session, cache, current_user, *args, **kwargs):
            pass

        def a_login_sync(session, cache, current_user):
            pass

        async def b_reg(session, cache, current_user, *args, **kwargs):
            pass

        async def b_select(session, cache, current_user, *args, **kwargs):
            pass

        module1 = SimpleNamespace(
            after_user_register=a_reg,
            after_user_login=a_login_sync,
        )
        module2 = SimpleNamespace(
            after_user_register=b_reg,
            after_user_select=b_select,
        )

        spec1 = MagicMock(); spec1.loader = MagicMock()
        spec2 = MagicMock(); spec2.loader = MagicMock()
        spec_from_file_mock.side_effect = [spec1, spec2]
        module_from_spec_mock.side_effect = [module1, module2]

        spec1.loader.exec_module.side_effect = lambda m: None
        spec2.loader.exec_module.side_effect = lambda m: None

        app = self._make_app()
        app.state.config = SimpleNamespace(
            ADDONS_LIST=["addon1", "addon2"],
            ADDONS_PATH="/addons",
        )

        init_hooks(app)

        self.assertListEqual(spec_from_file_mock.call_args_list, [
            call("addon1", "/addons/addon1.py"),
            call("addon2", "/addons/addon2.py"),
        ])
        self.assertListEqual(module_from_spec_mock.call_args_list, [
            call(spec1),
            call(spec2),
        ])
        spec1.loader.exec_module.assert_called_with(module1)
        spec2.loader.exec_module.assert_called_with(module2)

        hooks = app.state.hooks
        self.assertIn(HOOK_AFTER_USER_REGISTER, hooks)
        self.assertIn(HOOK_AFTER_USER_SELECT, hooks)

        self.assertEqual(hooks[HOOK_AFTER_USER_REGISTER], [a_reg, b_reg])
        self.assertEqual(hooks[HOOK_AFTER_USER_SELECT], [b_select])

        self.assertTrue("after_user_login" not in hooks
                        or len(hooks["after_user_login"]) == 0)

    @patch("app.hook.importlib.util.module_from_spec")
    @patch("app.hook.importlib.util.spec_from_file_location")
    async def test_addon_name_normalization(self, spec_from_file_mock,
                                            module_from_spec_mock):
        async def reg(session, cache, current_user, *args, **kwargs):
            pass

        module_a = SimpleNamespace(after_user_register=reg)
        module_b = SimpleNamespace(after_user_register=reg)

        spec_a = MagicMock(); spec_a.loader = MagicMock()
        spec_b = MagicMock(); spec_b.loader = MagicMock()
        spec_from_file_mock.side_effect = [spec_a, spec_b]
        module_from_spec_mock.side_effect = [module_a, module_b]
        spec_a.loader.exec_module.side_effect = lambda m: None
        spec_b.loader.exec_module.side_effect = lambda m: None

        app = self._make_app()
        app.state.config = SimpleNamespace(ADDONS_LIST=["a", "b.py"],
                                           ADDONS_PATH="/addons")

        init_hooks(app)

        self.assertListEqual(spec_from_file_mock.call_args_list, [
            call("a", "/addons/a.py"),
            call("b", "/addons/b.py"),
        ])
