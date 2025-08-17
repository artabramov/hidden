"""
Provides a lightweight context system based on ContextVar that
stores per-request variables and exposes them through a simple
attribute-style API.
"""

from typing import Any, Dict
from contextvars import ContextVar

# ContextVar used to store per-request dictionary of variables.
_local: ContextVar[Dict[str, Any]] = ContextVar("local_context_vars")


def _get_vars() -> Dict[str, Any]:
    """
    Returns the current dictionary of context variables, initializing
    and storing an empty dictionary in the ContextVar if none exists
    for the active execution context.
    """
    try:
        return _local.get()
    except LookupError:
        d: Dict[str, Any] = {}
        _local.set(d)
        return d


class Context:
    """
    Exposes request-scoped variables via attribute access by storing
    values in a ContextVar-backed dictionary and retrieving them within
    the current execution context.
    """
    def __setattr__(self, key: str, value: Any) -> None:
        """Set a context variable by assigning it as an attribute."""
        vars = _get_vars()
        new_vars = dict(vars)
        new_vars[key] = value
        _local.set(new_vars)

    def __getattr__(self, key: str) -> Any:
        """Retrieve a context variable by attribute access."""
        return _get_vars().get(key)


def get_context() -> Context:
    """
    Returns a Context instance bound to the current execution context
    for convenient attribute-style access to request-scoped variables.
    """
    return Context()
