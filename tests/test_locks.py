# tests/test_locks.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import unittest

from app.locks import LockManager, lock_manager


class TestLockManager(unittest.IsolatedAsyncioTestCase):
    def test_exposes_process_wide_manager(self):
        self.assertIsInstance(lock_manager, LockManager)

    async def test_releases_lock_when_body_fails(self):
        manager = LockManager()

        with self.assertRaises(RuntimeError):
            async with manager.lock():
                self.assertTrue(manager._lock.locked())
                raise RuntimeError("fail")

        self.assertFalse(manager._lock.locked())

    async def test_lock_excludes_concurrent_callers(self):
        manager = LockManager()
        started = asyncio.Event()
        release = asyncio.Event()
        acquired = asyncio.Event()

        async def hold():
            async with manager.lock():
                started.set()
                await release.wait()

        async def wait_for_lock():
            async with manager.lock():
                acquired.set()

        holder = asyncio.create_task(hold())
        await started.wait()
        waiter = asyncio.create_task(wait_for_lock())
        await asyncio.sleep(0)

        self.assertTrue(manager._lock.locked())
        self.assertFalse(acquired.is_set())

        release.set()
        await waiter
        await holder
        self.assertFalse(manager._lock.locked())
