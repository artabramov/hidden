# app/context.py
# SPDX-License-Identifier: GPL-3.0-only

from contextvars import ContextVar
from typing import Any

# NOTE (ADR-18): Request context is a per-task key-value store.
# It uses ContextVar to isolate state between concurrent execution
# contexts. A shallow copy is created on each write to avoid mutating
# shared state. By default, the context is expected to contain:
# 1. request_start_time - timestamp when the request processing started
# 2. request_uuid - identifier of the current request
# 3. current_user_id - identifier of the current user

_context: ContextVar[dict[str, Any]] = ContextVar(
    "context",
    default={},
)


def get_context_var(name: str, default: Any = None) -> Any:
    """
    Return a value from the current context by key.
    If the key is not present, return the provided default.
    """
    return _context.get().get(name, default)


def set_context_var(name: str, value: Any) -> None:
    """
    Set a value in the current context by key.
    Creates a shallow copy to preserve isolation between contexts.
    """
    ctx = _context.get().copy()
    ctx[name] = value
    _context.set(ctx)


def reset_context() -> None:
    """
    Reset the current context to an empty state.
    Intended to be called at the beginning and end of a request.
    """
    _context.set({})
