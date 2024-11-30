"""
The module provides functionality for loading and registering hooks from
enabled plugin modules. The hooks are registered by discovering functions
in the plugin modules and adding them to the context for later use.
"""

import os
import importlib.util
import inspect
from app.context import get_context
from app.config import get_config
from app.log import get_log

log = get_log()
ctx = get_context()
cfg = get_config()


async def load_hooks():
    """
    Loads and registers functions from plugin modules as hooks. The
    plugin modules are specified in the configuration, and their
    functions are registered by name in the context's hooks dictionary.
    Errors are  logged if the plugin modules fail to load.
    """
    ctx.hooks = {}

    # Load and register functions from plugin modules.
    filenames = [file + ".py" for file in cfg.PLUGINS_ENABLED]
    for filename in filenames:
        module_name = filename.split(".")[0]
        module_path = os.path.join(cfg.PLUGINS_BASE_PATH, filename)

        try:
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

        except Exception as e:
            log.debug("Hook error; filename=%s; e=%s;" % (filename, str(e)))
            raise e
