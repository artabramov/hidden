# app/hooks.py
# SPDX-License-Identifier: SSPL-1.0

import importlib
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from app.events import Events as E

# NOTE (ADR-30): Hooks and extensions trust model.
# Extensions are loaded via environment configuration (.env) and,
# once enabled, are treated as part of the application within the
# same security boundaries. They do not affect operation control
# flow, but have full access to the database and internal state.
# This is a flexible mechanism, but unsafe extensions can introduce
# security vulnerabilities and must be used with care.

# NOTE (ADR-31): Hooks executed after the main operation is committed.
# They may perform additional side effects, including database changes,
# but do not participate in the original transaction and cannot affect
# its outcome.

# NOTE (ADR-32): Hooks manage their own transactions.
# Any database changes performed inside a hook must be explicitly
# committed by the extension.

logger = logging.getLogger(__name__)
Hook = Callable[[AsyncSession | None, Any], Awaitable[Any]]

ALLOWED_HOOK_EVENTS = {
    E.CIPHERDIR_CREATE_COMPLETED,
    E.CIPHERDIR_MOUNT_COMPLETED,
    E.CIPHERDIR_UNMOUNT_COMPLETED,
    E.CIPHERDIR_PASSWORD_CHANGE_COMPLETED,
    E.LOCKDOWN_ENABLE_COMPLETED,
    E.LOCKDOWN_DISABLE_COMPLETED,
    E.USER_REGISTER_COMPLETED,
    E.USER_LOGIN_COMPLETED,
    E.USER_TOKEN_ISSUE_COMPLETED,
    E.USER_TOKEN_INVALIDATE_COMPLETED,
    E.USER_TOTP_RECOVER_COMPLETED,
    E.USER_SELECT_COMPLETED,
    E.USER_UPDATE_COMPLETED,
    E.USER_PASSWORD_CHANGE_COMPLETED,
    E.USER_RECOVERY_CODE_ROTATE_COMPLETED,
    E.USER_ROLE_CHANGE_COMPLETED,
    E.USER_LIST_COMPLETED,
    E.FOLDER_CREATE_COMPLETED,
    E.FOLDER_SELECT_COMPLETED,
    E.FOLDER_UPDATE_COMPLETED,
    E.FOLDER_DELETE_COMPLETED,
    E.FOLDER_LIST_COMPLETED,
    E.FOLDER_WRITE_PROTECT_COMPLETED,
    E.FILE_UPLOAD_COMPLETED,
    E.FILE_DOWNLOAD_COMPLETED,
    E.FILE_SELECT_COMPLETED,
    E.FILE_UPDATE_COMPLETED,
    E.FILE_STARRED_CHANGE_COMPLETED,
    E.FILE_MOVE_COMPLETED,
    E.FILE_ROTATE_COMPLETED,
    E.FILE_FLIP_COMPLETED,
    E.FILE_EDIT_COMPLETED,
    E.FILE_DELETE_COMPLETED,
    E.FILE_THUMBNAIL_RETRIEVE_COMPLETED,
    E.TAG_ADD_COMPLETED,
    E.TAG_DELETE_COMPLETED,
    E.TAG_LIST_COMPLETED,
    E.FILE_LIST_COMPLETED,
    E.COMMENT_CREATE_COMPLETED,
    E.COMMENT_UPDATE_COMPLETED,
    E.COMMENT_DELETE_COMPLETED,
    E.VARIABLE_SET_COMPLETED,
    E.VARIABLE_GET_COMPLETED,
    E.VARIABLE_DELETE_COMPLETED,
    E.VARIABLE_LIST_COMPLETED,
    E.AUDIT_LIST_COMPLETED,
}


class HookManager:
    """
    Registers and emits hooks for named events. Loads hook registrations
    from configured extensions and executes them sequentially after the
    main transaction has already succeeded (or after a control-plane
    operation that does not use an ORM transaction). Hook failures are
    logged and do not interrupt other hooks.
    """

    def __init__(self) -> None:
        self._hooks: dict[str, list[Hook]] = defaultdict(list)
        self._loaded = False

    def on(self, event: str, hook: Hook) -> None:
        """
        Registers a hook for the specified event.
        Hooks are executed in registration order.
        """
        if event not in ALLOWED_HOOK_EVENTS:
            raise ValueError(f"unknown hook event: {event}")

        self._hooks[event].append(hook)

    async def emit(
        self,
        event: str,
        session: AsyncSession | None = None,
        obj: Any = None,
    ) -> None:
        """
        Emits an event and executes all registered hooks.
        Exceptions are logged and do not interrupt execution.
        """
        if event not in ALLOWED_HOOK_EVENTS:
            raise ValueError(f"unknown hook event: {event}")

        for hook in self._hooks.get(event, []):
            try:
                await hook(session, obj)

            except Exception:
                logger.exception("hook execution failed")

    def load_extensions(self) -> None:
        """
        Loads and registers hooks from configured extensions.
        Ensures extensions are loaded only once.
        """
        if self._loaded:
            return

        config = get_config()

        for extension_name in config.ENABLED_EXTENSIONS_LIST:
            module_name = f"extensions.{extension_name}"
            module = importlib.import_module(module_name)

            register = getattr(module, "register", None)
            if not callable(register):
                logger.warning("extension skipped module=%s", module_name)
                continue

            register(self)
            logger.info("extension loaded module=%s", module_name)

        self._loaded = True


hooks = HookManager()
