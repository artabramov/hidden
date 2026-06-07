# tests/security/test_cipherdir.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
import time
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from app.security import cipherdir as cipherdir_module


def _reset_gate_state() -> None:
    cipherdir_module._last_attempt_monotonic = 0.0
    cipherdir_module._gate_lock = asyncio.Lock()


class TestIsMasterPasswordAttemptThrottled(IsolatedAsyncioTestCase):
    """Tests for is_master_password_attempt_throttled (cipherdir)."""

    def setUp(self) -> None:
        super().setUp()
        _reset_gate_state()

    def tearDown(self) -> None:
        _reset_gate_state()
        super().tearDown()

    def test_monotonic_returns_real_clock_value(self) -> None:
        before = time.monotonic()
        value = cipherdir_module._monotonic()
        after = time.monotonic()
        self.assertIsInstance(value, float)
        self.assertGreaterEqual(value, before)
        self.assertLessEqual(value, after)

    async def test_first_attempt_not_throttled(self) -> None:
        with patch.object(
            cipherdir_module,
            "MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS",
            60.0,
        ):
            with patch(
                "app.security.cipherdir._monotonic",
                return_value=10_000.0,
            ):
                throttled = (
                    cipherdir_module.is_master_password_attempt_throttled
                )
                result = await throttled()

        self.assertFalse(result)
        self.assertEqual(
            cipherdir_module._last_attempt_monotonic,
            10_000.0,
        )

    async def test_second_attempt_inside_interval_throttled(self) -> None:
        with patch.object(
            cipherdir_module,
            "MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS",
            60.0,
        ):
            with patch(
                "app.security.cipherdir._monotonic",
                side_effect=[1_000.0, 1_000.5],
            ):
                throttled = (
                    cipherdir_module.is_master_password_attempt_throttled
                )
                first = await throttled()
                second = await throttled()

        self.assertFalse(first)
        self.assertTrue(second)
        self.assertEqual(cipherdir_module._last_attempt_monotonic, 1_000.0)

    async def test_attempt_after_interval_not_throttled(self) -> None:
        with patch.object(
            cipherdir_module,
            "MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS",
            10.0,
        ):
            with patch(
                "app.security.cipherdir._monotonic",
                side_effect=[500.0, 511.0],
            ):
                throttled = (
                    cipherdir_module.is_master_password_attempt_throttled
                )
                first = await throttled()
                second = await throttled()

        self.assertFalse(first)
        self.assertFalse(second)
        self.assertEqual(cipherdir_module._last_attempt_monotonic, 511.0)

    async def test_throttled_call_does_not_move_window(self) -> None:
        with patch.object(
            cipherdir_module,
            "MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS",
            10.0,
        ):
            with patch(
                "app.security.cipherdir._monotonic",
                side_effect=[100.0, 105.0, 111.0],
            ):
                throttled = (
                    cipherdir_module.is_master_password_attempt_throttled
                )
                self.assertFalse(await throttled())
                self.assertTrue(await throttled())
                self.assertFalse(await throttled())

        self.assertEqual(cipherdir_module._last_attempt_monotonic, 111.0)

    async def test_concurrent_callers_one_throttled_one_not(self) -> None:
        with patch.object(
            cipherdir_module,
            "MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS",
            10.0,
        ):
            with patch(
                "app.security.cipherdir._monotonic",
                side_effect=[50.0, 50.0],
            ):
                throttled = (
                    cipherdir_module.is_master_password_attempt_throttled
                )
                outcomes = await asyncio.gather(
                    throttled(),
                    throttled(),
                )

        self.assertEqual(sorted(outcomes), [False, True])


if __name__ == "__main__":
    unittest.main()
