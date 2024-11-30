"""
Manages context variables using Python's contextvars module, allowing
for context-specific data storage in asynchronous applications. Defines
a Context class to set and retrieve context variables, mimicking a
thread-local storage approach that also works with asyncio tasks.
"""

from contextvars import ContextVar
from typing import Any

local_context_vars: ContextVar[dict] = ContextVar(
    "local_context_vars", default={})


class Context:
    """
    The Context class provides a mechanism to manage context-specific
    variables using Python's contextvars module. It allows setting and
    retrieving context variables, which can be useful for storing data
    specific to the current asynchronous task or operation, similar
    to thread-local storage but compatible with asyncio.
    """

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Set a value for a context variable. If the key does not
        exist, it is created. This method updates the context
        variable dictionary with the provided key-value pair.
        """
        vars = local_context_vars.get()
        vars[key] = value
        local_context_vars.set(vars)

    def __getattr__(self, key: str) -> Any:
        """
        Retrieve the value of a context variable by its key. If the
        key does not exist, it returns None. This method accesses
        the current context variable dictionary and returns the
        associated value.
        """
        vars = local_context_vars.get()
        return vars.get(key)


def get_context():
    """
    Create and return a new instance of the Context class. This function
    provides a way to access context variables, which are useful for
    maintaining context across asynchronous tasks and threads.
    """
    return Context()
