# app/locks.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator


class LockManager:
    """
    Serialize in-process operations that must not run concurrently
    using a single process-wide asynchronous lock.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def lock(self) -> AsyncIterator[None]:
        """
        Acquire the process-wide exclusive lock for the duration
        of the managed operation.
        """
        async with self._lock:
            yield


lock_manager = LockManager()
