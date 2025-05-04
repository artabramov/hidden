
"""
Defines a context class to set and retrieve context variables, mimicking
a thread-local storage approach that also works with asyncio tasks.
"""

from typing import Any
from contextvars import ContextVar

local_context_vars: ContextVar[dict] = ContextVar(
    "local_context_vars", default={})


class Context:
    """
    Provides a mechanism to manage context-specific variables using
    contextvars module. It allows setting and retrieving context
    variables, which can be useful for storing data specific to the
    current asynchronous task or operation, similar to thread-local
    storage but compatible with asyncio.
    """

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Updates the context variable dictionary with the provided
        key-value pair. If the key does not exist, it is created.
        """
        vars = local_context_vars.get()
        vars[key] = value
        local_context_vars.set(vars)

    def __getattr__(self, key: str) -> Any:
        """
        Retrieve the value of a context variable by its key. If the
        key does not exist, it returns None.
        """
        vars = local_context_vars.get()
        return vars.get(key)


def get_context():
    """Return a new instance of the context."""
    return Context()
