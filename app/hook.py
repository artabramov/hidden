"""
The module defines a system for executing various hooks based on
specific actions within the app. The hook class operates with event
operations.
"""

import os
import importlib.util
import inspect
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.config import get_config
from app.context import get_context

cfg = get_config()
ctx = get_context()

HOOK_AFTER_TOKEN_RETRIEVE = "after_token_retrieve"
HOOK_AFTER_TOKEN_INVALIDATE = "after_token_invalidate"

HOOK_AFTER_USER_REGISTER = "after_user_register"
HOOK_AFTER_USER_LOGIN = "after_user_login"
HOOK_AFTER_USER_SELECT = "after_user_select"
HOOK_AFTER_USER_UPDATE = "after_user_update"
HOOK_AFTER_USER_PASSWORD = "after_user_password"
HOOK_AFTER_USER_ROLE = "after_user_role"
HOOK_AFTER_USER_DELETE = "after_user_delete"
HOOK_AFTER_USER_LIST = "after_user_list"
HOOK_AFTER_USERPIC_UPLOAD = "after_userpic_upload"
HOOK_AFTER_USERPIC_DELETE = "after_userpic_delete"

HOOK_AFTER_COLLECTION_INSERT = "after_collection_insert"
HOOK_AFTER_COLLECTION_SELECT = "after_collection_select"
HOOK_AFTER_COLLECTION_UPDATE = "after_collection_update"
HOOK_AFTER_COLLECTION_DELETE = "after_collection_delete"
HOOK_AFTER_COLLECTION_LIST = "after_collection_list"

HOOK_AFTER_DOCUMENT_UPLOAD = "after_document_upload"
HOOK_AFTER_DOCUMENT_SELECT = "after_document_select"
HOOK_AFTER_DOCUMENT_UPDATE = "after_document_update"
HOOK_AFTER_DOCUMENT_MOVE = "after_document_move"
HOOK_AFTER_DOCUMENT_DELETE = "after_document_delete"
HOOK_AFTER_DOCUMENT_LIST = "after_document_list"

HOOK_AFTER_TAG_INSERT = "after_tag_insert"
HOOK_AFTER_TAG_DELETE = "after_tag_delete"
HOOK_AFTER_TAG_LIST = "after_tag_list"

HOOK_AFTER_SETTING_INSERT = "after_setting_insert"
HOOK_AFTER_SETTING_LIST = "after_setting_list"

HOOK_AFTER_SECRET_RETRIEVE = "after_secret_retrieve"
HOOK_AFTER_SECRET_DELETE = "after_secret_delete"

HOOK_AFTER_LOCK_CREATE = "after_lock_create"
HOOK_AFTER_LOCK_RETRIEVE = "after_lock_retrieve"

HOOK_AFTER_TELEMETRY_RETRIEVE = "after_telemetry_retrieve"

HOOK_ON_EXECUTE = "on_execute"


class Hook:
    """
    Manages and executes hooks for handling post-event operations within
    the app. The class initializes with entity manager, cache manager,
    request, and optionally current user. The execute method runs the
    appropriate hook functions based on the specified hook action,
    processing data as required and returning the result.
    """

    def __init__(self, session: AsyncSession, cache: Redis,
                 current_user: User = None):
        self.session = session
        self.cache = cache
        self.current_user = current_user

    async def call(self, hook: str, *args, **kwargs):
        if hook in ctx.hooks:
            hook_functions = ctx.hooks[hook]
            for func in hook_functions:
                await func(self.session, self.cache, self.current_user,
                           *args, **kwargs)


async def init_hooks():
    """
    Loads and registers functions from addon modules as hooks. The
    addon modules are specified in the configuration, and their
    functions are registered by name in the context's hooks dictionary.
    """
    ctx.hooks = {}

    # Load and register functions from addon modules.
    filenames = [file + ".py" for file in cfg.ADDONS_ENABLED]
    for filename in filenames:
        module_name = filename.split(".")[0]
        module_path = os.path.join(cfg.ADDONS_PATH, filename)

        # Load the module from the specified file path.
        spec = importlib.util.spec_from_file_location(
            module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Register functions from the module as hooks.
        func_names = [attr for attr in dir(module)
                      if inspect.isfunction(getattr(module, attr))]
        for func_name in func_names:
            func = getattr(module, func_name)
            if func_name not in ctx.hooks:
                ctx.hooks[func_name] = [func]
            else:
                ctx.hooks[func_name].append(func)
