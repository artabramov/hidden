"""
This module defines a system for executing various hooks based on
specific actions within the application. It includes the Hook class,
which orchestrates post-event operations by interacting with
EntityManager and CacheManager. The H enumeration specifies different
hook types, and the Hook class manages their execution, handling actions
related to user management, collections, documents, comments, downloads,
and favorites. This setup enables asynchronous processing and integrates
seamlessly with session and caching systems to ensure efficient state
management and responsiveness to application events.
"""

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.models.user_model import User
from app.context import get_context

ctx = get_context()


class Hook:
    """
    Manages and executes various hooks for handling post-event
    operations within the application. This class initializes with
    necessary components such as an entity manager, cache manager,
    request, and current user. The execute method runs the appropriate
    hook functions based on the specified hook action, processing data
    as required and returning the result.
    """

    def __init__(self, session: AsyncSession, cache: Redis,
                 current_user: User = None):
        """
        Initializes the Hook class with an entity manager,
        cache manager, request, and current user. The entity manager
        is created from the provided session, and the cache manager is
        created from the provided Redis instance. The current user is
        optional and can be used to provide context for the hook
        execution.
        """
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.current_user = current_user

    async def do(self, hook: str, *args, **kwargs):
        """
        Executes the specified hook action by calling the associated
        functions with the provided entity manager, cache manager,
        request, current user, and data. The hook functions are
        retrieved from the context based on the hook action value and
        are invoked sequentially.
        """
        if hook in ctx.hooks:
            hook_functions = ctx.hooks[hook]
            for func in hook_functions:
                await func(self.entity_manager, self.cache_manager,
                           self.current_user, *args, **kwargs)
