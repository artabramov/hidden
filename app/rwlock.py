import asyncio
from contextlib import asynccontextmanager
from collections import defaultdict

class RWLock:
    """
    Asyncio-friendly readers-writer lock with writer preference.
    - Multiple readers can hold the lock concurrently.
    - Writers get exclusive access.
    - New readers are blocked when a writer is waiting (prevents writer starvation).
    """
    def __init__(self):
        self._readers = 0
        self._readers_cond = asyncio.Condition()
        self._writer_lock = asyncio.Lock()
        self._writers_waiting = 0

    @asynccontextmanager
    async def read(self):
        # Block new readers if a writer is active or waiting.
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
        # Signal writer intent first to block new readers.
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
