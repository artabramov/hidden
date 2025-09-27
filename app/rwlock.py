"""Asyncio reader–writer lock with writer preference."""

import asyncio
from contextlib import asynccontextmanager


class RWLock:
    """
    Asyncio-friendly readers-writer lock with writer preference:
    multiple readers may proceed concurrently, writers acquire
    exclusive access, and new readers are blocked while any writer
    is active or waiting. Non-reentrant and in-process only;
    cancellation-safe.
    """

    def __init__(self):
        self._readers = 0
        self._readers_cond = asyncio.Condition()
        self._writer_lock = asyncio.Lock()
        self._writers_waiting = 0

    @asynccontextmanager
    async def read(self):
        """
        Acquire a shared read lock: waits while a writer is active or
        queued, then yields; releases on exit and wakes waiters when
        the last reader leaves.
        """
        async with self._readers_cond:
            while self._writer_lock.locked() or self._writers_waiting > 0:
                await self._readers_cond.wait()
            self._readers += 1
        try:
            yield
        finally:
            async with self._readers_cond:
                self._readers -= 1
                if self._readers == 0:
                    self._readers_cond.notify_all()

    @asynccontextmanager
    async def write(self):
        """
        Acquire an exclusive write lock: announces writer intent to
        block new readers, waits for current readers to drain, then
        yields; releases on exit and wakes pending readers/writers.
        """
        self._writers_waiting += 1
        try:
            await self._writer_lock.acquire()
            # Wait for all current readers to drain.
            async with self._readers_cond:
                while self._readers > 0:
                    await self._readers_cond.wait()
            yield
        finally:
            self._writer_lock.release()
            self._writers_waiting -= 1
            # Wake everyone: next writer or pending readers.
            async with self._readers_cond:
                self._readers_cond.notify_all()
