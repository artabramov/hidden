"""
Example addon module for handling event hook functions triggered by
corresponding events within the app. Each function is associated with
a specific event and is designed to be executed when that event occurs.
Functions may include additional logic such as event logging, updating
the database, managing the cache, performing file or network operations,
interacting with third-party apps, and other actions.
"""

from typing import List
from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.collection import Collection


async def after_token_retrieve(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a token is retrieved (issued)."""
    ...


async def after_token_invalidate(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a token is invalidated (logout)."""
    ...


async def after_user_register(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a user is registered."""
    ...


async def after_user_role(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, user: User):
    """Executes after a user role or active status is changed."""
    ...


async def after_user_password(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a user password is changed."""
    ...


async def after_user_login(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a user logs in."""
    ...


async def after_user_select(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, user: User):
    """Executes after a user is retrieved."""
    ...


async def after_user_update(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a user is updated."""
    ...


async def after_user_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, user: User):
    """Executes after a user is deleted."""
    ...


async def after_user_list(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, users: List[User], users_count: int):
    """Executes after a list of users is retrieved."""
    ...


async def after_userpic_upload(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a userpic is uploaded."""
    ...


async def after_userpic_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User):
    """Executes after a userpic is deleted."""
    ...


async def after_userpic_retrieve(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, user: User):
    """Executes after a userpic is retrieved."""
    ...


async def after_collection_insert(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, collection: Collection):
    """Executes after a collection is created."""
    ...
