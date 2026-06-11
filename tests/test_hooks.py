# tests/test_hooks.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.events import Events as E
from app.hooks import ALLOWED_HOOK_EVENTS, HookManager


class TestAllowedHookEvents(unittest.TestCase):

    def test_includes_new_completed_events(self):
        self.assertIn(E.FILE_UPDATE_COMPLETED, ALLOWED_HOOK_EVENTS)
        self.assertIn(E.FILE_STARRED_CHANGE_COMPLETED, ALLOWED_HOOK_EVENTS)


class TestHookManager(unittest.IsolatedAsyncioTestCase):

    async def test_registers_and_emits_hook(self):
        manager = HookManager()
        session = AsyncMock()
        obj = MagicMock()

        hook = AsyncMock()

        manager.on(E.FILE_UPDATE_COMPLETED, hook)
        await manager.emit(E.FILE_UPDATE_COMPLETED, session, obj)

        hook.assert_awaited_once_with(session, obj)

    async def test_executes_hooks_in_registration_order(self):
        manager = HookManager()
        session = AsyncMock()
        obj = MagicMock()
        calls = []

        async def first_hook(session, obj):
            calls.append("first")

        async def second_hook(session, obj):
            calls.append("second")

        manager.on(E.FILE_UPDATE_COMPLETED, first_hook)
        manager.on(E.FILE_UPDATE_COMPLETED, second_hook)

        await manager.emit(E.FILE_UPDATE_COMPLETED, session, obj)

        self.assertEqual(calls, ["first", "second"])

    async def test_hook_failure_does_not_stop_next_hook(self):
        manager = HookManager()
        session = AsyncMock()
        obj = MagicMock()

        failing_hook = AsyncMock(side_effect=RuntimeError("boom"))
        next_hook = AsyncMock()

        manager.on(E.FILE_UPDATE_COMPLETED, failing_hook)
        manager.on(E.FILE_UPDATE_COMPLETED, next_hook)

        with patch("app.hooks.logger.exception") as exception_mock:
            await manager.emit(E.FILE_UPDATE_COMPLETED, session, obj)

        failing_hook.assert_awaited_once_with(session, obj)
        next_hook.assert_awaited_once_with(session, obj)
        exception_mock.assert_called_once_with("hook execution failed")

    async def test_emit_allows_none_object(self):
        manager = HookManager()
        session = AsyncMock()

        hook = AsyncMock()

        manager.on(E.FILE_UPDATE_COMPLETED, hook)
        await manager.emit(E.FILE_UPDATE_COMPLETED, session)

        hook.assert_awaited_once_with(session, None)

    async def test_emit_allows_none_session(self):
        manager = HookManager()
        hook = AsyncMock()

        manager.on(E.FILE_UPDATE_COMPLETED, hook)
        await manager.emit(E.FILE_UPDATE_COMPLETED)

        hook.assert_awaited_once_with(None, None)

    async def test_emit_unknown_event_raises_value_error(self):
        manager = HookManager()
        session = AsyncMock()

        with self.assertRaises(ValueError):
            await manager.emit("unknown:event", session)

    async def test_on_unknown_event_raises_value_error(self):
        manager = HookManager()
        hook = AsyncMock()

        with self.assertRaises(ValueError):
            manager.on("unknown:event", hook)


class TestHookManagerLoadExtensions(unittest.TestCase):

    def test_load_extensions_imports_and_registers_enabled_extensions(self):
        manager = HookManager()

        config = SimpleNamespace(
            ENABLED_EXTENSIONS_LIST=["alpha", "beta"],
        )

        alpha_module = SimpleNamespace(register=MagicMock())
        beta_module = SimpleNamespace(register=MagicMock())
        logger_mock = MagicMock()

        def import_module(name):
            if name == "extensions.alpha":
                return alpha_module
            if name == "extensions.beta":
                return beta_module
            raise AssertionError(name)

        with (
            patch("app.hooks.get_config", return_value=config),
            patch("app.hooks.logger", logger_mock),
            patch(
                "app.hooks.importlib.import_module",
                side_effect=import_module,
            ) as import_mock,
        ):
            manager.load_extensions()

        self.assertTrue(manager._loaded)
        self.assertEqual(import_mock.call_count, 2)

        alpha_module.register.assert_called_once_with(manager)
        beta_module.register.assert_called_once_with(manager)

        self.assertEqual(logger_mock.info.call_count, 2)
        logger_mock.warning.assert_not_called()

    def test_load_extensions_skips_module_without_callable_register(self):
        manager = HookManager()

        config = SimpleNamespace(
            ENABLED_EXTENSIONS_LIST=["broken"],
        )

        module = SimpleNamespace(register=None)
        logger_mock = MagicMock()

        with (
            patch("app.hooks.get_config", return_value=config),
            patch("app.hooks.logger", logger_mock),
            patch(
                "app.hooks.importlib.import_module",
                return_value=module,
            ) as import_mock,
        ):
            manager.load_extensions()

        self.assertTrue(manager._loaded)

        import_mock.assert_called_once_with("extensions.broken")
        logger_mock.warning.assert_called_once_with(
            "extension skipped module=%s",
            "extensions.broken",
        )
        logger_mock.info.assert_not_called()

    def test_load_extensions_runs_only_once(self):
        manager = HookManager()

        config = SimpleNamespace(
            ENABLED_EXTENSIONS_LIST=["alpha"],
        )

        module = SimpleNamespace(register=MagicMock())

        with (
            patch("app.hooks.get_config", return_value=config) as config_mock,
            patch(
                "app.hooks.importlib.import_module",
                return_value=module,
            ) as import_mock,
        ):
            manager.load_extensions()
            manager.load_extensions()

        config_mock.assert_called_once()
        import_mock.assert_called_once_with("extensions.alpha")
        module.register.assert_called_once_with(manager)
