# app/context.py
# SPDX-License-Identifier: Apache-2.0

from contextvars import ContextVar
from typing import Any

_context: ContextVar[dict[str, Any]] = ContextVar(
    "context",
    default={},
)


def get_context_var(name: str, default: Any = None) -> Any:
    """
    Return a value from the current context by name,
    or the provided default if the value is not set.
    """
    return _context.get().get(name, default)


def set_context_var(name: str, value: Any) -> None:
    """
    Set a value in the current context using a shallow copy
    to preserve isolation between contexts.
    """
    ctx = _context.get().copy()
    ctx[name] = value
    _context.set(ctx)


def reset_context() -> None:
    """
    Reset the current context to an empty state. Intended
    to be called at the beginning and end of a request.
    """
    _context.set({})
