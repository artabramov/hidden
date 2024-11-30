"""
The module defines a scheduler that periodically executes a scheduled
hook action. The scheduler runs in an infinite loop, fetching a session
and cache instance from the database and cache generators, respectively.
Once the resources are obtained, the Hook class is instantiated, and the
hook action is executed.
"""

import asyncio
from app.database import get_session
from app.cache import get_cache
from app.config import get_config
from app.constants import HOOK_ON_SCHEDULE
from app.hooks import Hook

cfg = get_config()


async def scheduler():
    """
    The function continuously runs an asynchronous loop that
    periodically retrieves a session and cache instance, then executes
    a scheduled task using the Hook class based on the HOOK_ON_SCHEDULE
    event. After executing the task, it ensures the session and cache
    are properly closed and then sleeps for a specified interval
    before repeating the process. This function is designed to run
    indefinitely, enabling periodic background tasks to be performed
    at regular intervals.
    """
    while True:
        session_gen = get_session()
        cache_gen = get_cache()

        try:
            async for session in session_gen:
                async for cache in cache_gen:
                    hook = Hook(session, cache)
                    await hook.do(HOOK_ON_SCHEDULE)

        finally:
            await session.close()
            await cache.close()

        await asyncio.sleep(cfg.APP_SCHEDULER_RATE)
