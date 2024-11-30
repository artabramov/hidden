"""
The module provides a decorator for timing and logging the execution of
asynchronous functions. The decorator records the duration of function
execution, along with function details, arguments, and results. It also
handles and logs exceptions, making it useful for performance monitoring
and debugging by providing detailed insights into function behavior and
execution time.
"""

import time
import functools
from typing import Callable, Any
from app.log import get_log

log = get_log()


def timed(func: Callable) -> Callable:
    """
    Decorator for measuring and logging the execution time of
    asynchronous functions. It logs the duration, function name, module,
    arguments, keyword arguments, and result of the function call. In
    case of an exception, it logs the error along with the elapsed time,
    function details, and exception message. Useful for performance
    monitoring and debugging.
    """
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        try:
            start_time = time.time()
            res = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time

            log.debug("Function executed; module=%s; function=%s; "
                      "elapsed_time=%s; args=%s; kwargs=%s; res=%s;" % (
                          func.__module__, func.__qualname__, elapsed_time,
                          str(args), str(kwargs), str(res)))

            return res

        except Exception as e:
            elapsed_time = time.time() - start_time

            log.error(
                "Function failed; module=%s; function=%s; elapsed_time=%s; "
                "args=%s; kwargs=%s; e=%s;" % (
                    func.__module__, func.__qualname__,
                    "{0:.10f}".format(elapsed_time), str(args), str(kwargs),
                    str(e)))

            raise e

    return wrapped
