"""
Provides an application hook system: loads add-on modules listed in the
config, discovers async handlers named after known hooks, and registers
them for post-event execution.
"""

import os
import importlib.util
import inspect
from fastapi import FastAPI, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

# TODO: Replace HOOK_* constant list with a dataclass.

HOOK_AFTER_TOKEN_RETRIEVE = "after_token_retrieve"  # nosec: B105
HOOK_AFTER_TOKEN_INVALIDATE = "after_token_invalidate"  # nosec: B105

HOOK_AFTER_USER_REGISTER = "after_user_register"
HOOK_AFTER_USER_LOGIN = "after_user_login"
HOOK_AFTER_USER_ROLE = "after_user_role"
HOOK_AFTER_USER_PASSWORD = "after_user_password"  # nosec: B105
HOOK_AFTER_USER_SELECT = "after_user_select"
HOOK_AFTER_USER_UPDATE = "after_user_update"
HOOK_AFTER_USER_DELETE = "after_user_delete"
HOOK_AFTER_USER_LIST = "after_user_list"
HOOK_AFTER_USERPIC_UPLOAD = "after_userpic_upload"
HOOK_AFTER_USERPIC_DELETE = "after_userpic_delete"
HOOK_AFTER_USERPIC_RETRIEVE = "after_userpic_retrieve"

HOOK_AFTER_COLLECTION_INSERT = "after_collection_insert"
HOOK_AFTER_COLLECTION_SELECT = "after_collection_select"
HOOK_AFTER_COLLECTION_UPDATE = "after_collection_update"
HOOK_AFTER_COLLECTION_DELETE = "after_collection_delete"
HOOK_AFTER_COLLECTION_LIST = "after_collection_list"

HOOK_AFTER_DOCUMENT_UPLOAD = "after_document_upload"
HOOK_AFTER_DOCUMENT_DOWNLOAD = "after_document_download"
HOOK_AFTER_DOCUMENT_SELECT = "after_document_select"
HOOK_AFTER_DOCUMENT_UPDATE = "after_document_update"
HOOK_AFTER_DOCUMENT_DELETE = "after_document_delete"
HOOK_AFTER_DOCUMENT_LIST = "after_document_list"
HOOK_AFTER_THUMBNAIL_RETRIEVE = "after_thumbnail_retrieve"
HOOK_AFTER_TAG_INSERT = "after_tag_insert"
HOOK_AFTER_TAG_DELETE = "after_tag_delete"

HOOK_AFTER_TELEMETRY_RETRIEVE = "after_telemetry_retrieve"

ENABLED_HOOKS = {
    HOOK_AFTER_TOKEN_RETRIEVE,
    HOOK_AFTER_TOKEN_INVALIDATE,

    HOOK_AFTER_USER_REGISTER,
    HOOK_AFTER_USER_LOGIN,
    HOOK_AFTER_USER_ROLE,
    HOOK_AFTER_USER_PASSWORD,
    HOOK_AFTER_USER_SELECT,
    HOOK_AFTER_USER_UPDATE,
    HOOK_AFTER_USER_DELETE,
    HOOK_AFTER_USER_LIST,
    HOOK_AFTER_USERPIC_UPLOAD,
    HOOK_AFTER_USERPIC_DELETE,
    HOOK_AFTER_USERPIC_RETRIEVE,

    HOOK_AFTER_COLLECTION_INSERT,
    HOOK_AFTER_COLLECTION_SELECT,
    HOOK_AFTER_COLLECTION_UPDATE,
    HOOK_AFTER_COLLECTION_DELETE,
    HOOK_AFTER_COLLECTION_LIST,

    HOOK_AFTER_DOCUMENT_UPLOAD,
    HOOK_AFTER_DOCUMENT_DOWNLOAD,
    HOOK_AFTER_DOCUMENT_SELECT,
    HOOK_AFTER_DOCUMENT_UPDATE,
    HOOK_AFTER_DOCUMENT_DELETE,
    HOOK_AFTER_DOCUMENT_LIST,
    HOOK_AFTER_THUMBNAIL_RETRIEVE,
    HOOK_AFTER_TAG_INSERT,
    HOOK_AFTER_TAG_DELETE,

    HOOK_AFTER_TELEMETRY_RETRIEVE,
}


class Hook:
    """
    Executes registered hook handlers from app state, passing the
    request session, Redis cache, the current user, and any extra
    arguments.
    """

    def __init__(self, request: Request, session: AsyncSession, cache: Redis,
                 current_user: User):
        """
        Binds to the app's hook registry and stores the session, cache,
        and optional current user for later execution.
        """
        self.request = request
        self.session = session
        self.cache = cache
        self.current_user = current_user

    async def call(self, hook: str, *args, **kwargs):
        """
        Runs all handlers registered for the given hook in order,
        passing session, cache, current user, and provided args/kwargs.
        """
        for func in self.request.app.state.hooks.get(hook, ()):
            try:
                await func(self.request, self.session, self.cache,
                           self.current_user, *args, **kwargs)
            except Exception:
                self.request.state.log.exception(
                    f"hook failed; hook={func.__name__};")


def init_hooks(app: FastAPI) -> None:
    """
    Builds the hook registry by importing add-on modules from the
    configured path and registering async functions whose names match
    constants in enabled hooks.
    """
    app.state.hooks = {}

    # Load and register functions from addon modules
    filenames = [f if f.endswith(".py") else f + ".py"
                 for f in app.state.config.ADDONS_LIST]

    for filename in filenames:
        module_name = os.path.splitext(os.path.basename(filename))[0]
        module_path = os.path.join(app.state.config.ADDONS_PATH, filename)

        # Load the module from the specified file path
        spec = importlib.util.spec_from_file_location(
            module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load addon: {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Register functions from the module as hooks
        for hook_name in ENABLED_HOOKS:
            func = getattr(module, hook_name, None)
            if func and inspect.iscoroutinefunction(func):
                app.state.hooks.setdefault(hook_name, []).append(func)
