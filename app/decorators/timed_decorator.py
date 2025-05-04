"""
The module provides a decorator for timing and logging the execution of
asynchronous functions. The decorator records the duration of function
execution, along with function details, arguments, and results. It also
handles and logs exceptions.
"""

import time
import functools
from typing import Callable, Any
from app.log import get_log

log = get_log()


def timed(func: Callable) -> Callable:
    """
    Decorator for asynchronous functions. It logs the duration,
    function name, module, arguments, and result of the call.
    """
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed_time = "{0:.6f}".format(time.time() - start_time)

            log.debug(
                f"Function executed; module={func.__module__}; "
                f"function={func.__qualname__}; elapsed_time={elapsed_time}; "
                f"args={str(args)}; kwargs={str(kwargs)}; res={str(result)};")

            return result

        except Exception as e:
            elapsed_time = "{0:.6f}".format(time.time() - start_time)

            log.error(
                f"Function failed; module={func.__module__}; "
                f"function={func.__qualname__}; elapsed_time={elapsed_time}; "
                f"args={str(args)}; kwargs={str(kwargs)}; e={str(e)};")

            raise e

    return wrapped
