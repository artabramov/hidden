# tests/dependencies/test_session.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

import app.dependencies.session as session_dep  # noqa: E402


class TestGetSession(unittest.IsolatedAsyncioTestCase):
    async def test_yields_session_and_closes_context(self):
        mock_sess = MagicMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_sess)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        factory = MagicMock(return_value=mock_cm)

        with patch("app.dependencies.session.SessionLocal", factory):
            items: list[MagicMock] = []
            async for s in session_dep.get_session():
                items.append(s)

        self.assertEqual(items, [mock_sess])
        factory.assert_called_once_with()
        mock_cm.__aenter__.assert_awaited_once()
        mock_cm.__aexit__.assert_awaited_once()

    async def test_second_iteration_raises_stop(self):
        mock_sess = MagicMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_sess)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        factory = MagicMock(return_value=mock_cm)

        with patch("app.dependencies.session.SessionLocal", factory):
            gen = session_dep.get_session()
            first = await anext(gen)
            self.assertIs(first, mock_sess)
            with self.assertRaises(StopAsyncIteration):
                await anext(gen)

        mock_cm.__aexit__.assert_awaited_once()
