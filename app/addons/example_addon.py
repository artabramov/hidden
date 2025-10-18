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
from app.models.folder import Folder
from app.models.file import File


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


async def after_folder_insert(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, folder: Folder):
    """Executes after a folder is created."""
    ...


async def after_folder_select(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, folder: Folder):
    """Executes after a folder is retrieved."""
    ...


async def after_folder_update(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, folder: Folder):
    """Executes after a folder is updated."""
    ...


async def after_folder_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, folder_id: int):
    """Executes after a folder is deleted."""
    ...


async def after_folder_list(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, folders: List[Folder],
        folders_count: int):
    """Executes after a folder list is retrieved."""
    ...


async def after_file_upload(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file: File):
    """Executes after a file is uploaded."""
    ...


async def after_file_download(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file: File, revision_number: int):
    """Executes after a file is downloaded."""
    ...


async def after_file_select(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file: File):
    """Executes after a file is retrieved."""
    ...


async def after_file_update(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file: File):
    """Executes after a file is updated."""
    ...


async def after_file_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file_id: int):
    """Executes after a file is deleted."""
    ...


async def after_file_list(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, files: List[File], files_count: int):
    """Executes after a file list is retrieved."""
    ...


async def after_thumbnail_retrieve(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file: File):
    """Executes after a file thumbnail is retrieved."""
    ...


async def after_tag_insert(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file: File, tag_value: str):
    """Executes after a file tag is added."""
    ...


async def after_tag_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, file: File, tag_value: str):
    """Executes after a tag is deleted."""
    ...


async def after_telemetry_retrieve(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, telemetry: dict):
    """Executes after telemetry is retrieved."""
    ...
