"""
Example addon module for handling event hook functions triggered
by corresponding events within the app. Each function is associated
with a specific event and is designed to be executed when that event
occurs. Functions may include additional logic such as event logging,
updating the database, managing the cache, performing file or network
operations, interacting with third-party apps, and other actions.
"""

from typing import List
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.tag_model import Tag
from app.models.setting_model import Setting


async def after_token_retrieve(
        session: AsyncSession, cache: Redis, current_user: User):
    """Executes after a token is retrieved."""
    ...


async def after_token_invalidate(
        session: AsyncSession, cache: Redis, current_user: User):
    """Executes after a token is invalidated."""
    ...


async def after_user_register(
        session: AsyncSession, cache: Redis, current_user: User):
    """Executes after a user is registered."""
    ...


async def after_user_login(
        session: AsyncSession, cache: Redis, current_user: User):
    """Executes after a user is logged in."""
    ...


async def after_user_select(
        session: AsyncSession, cache: Redis, current_user: User,
        user: User):
    """Executes after a user is selected."""
    ...


async def after_user_update(
        session: AsyncSession, cache: Redis, current_user: User,
        user: User):
    """Executes after a user is updated."""
    ...


async def after_user_password(
        session: AsyncSession, cache: Redis, current_user: User,
        user: User):
    """Executes after a user password is changed."""
    ...


async def after_user_role(
        session: AsyncSession, cache: Redis, current_user: User,
        user: User):
    """Executes after a user role is changed."""
    ...


async def after_user_delete(
        session: AsyncSession, cache: Redis, current_user: User,
        user: User):
    """Executes after a user is deleted."""
    ...


async def after_user_list(
        session: AsyncSession, cache: Redis, current_user: User,
        users: List[User], users_count: int):
    """Executes after a user list is retrieved."""
    ...


async def after_userpic_upload(
        session: AsyncSession, cache: Redis, current_user: User,
        user: User):
    """Executes after a userpic is uploaded."""
    ...


async def after_userpic_delete(
        session: AsyncSession, cache: Redis, current_user: User,
        user: User):
    """Executes after a userpic is deleted."""
    ...


async def after_collection_insert(
        session: AsyncSession, cache: Redis, current_user: User,
        collection: Collection):
    """Executes after a collection is created."""
    ...


async def after_collection_select(
        session: AsyncSession, cache: Redis, current_user: User,
        collection: Collection):
    """Executes after a collection is selected."""
    ...


async def after_collection_update(
        session: AsyncSession, cache: Redis, current_user: User,
        collection: Collection):
    """Executes after a collection is updated."""
    ...


async def after_collection_delete(
        session: AsyncSession, cache: Redis, current_user: User,
        collection: Collection):
    """Executes after a collection is deleted."""
    ...


async def after_collection_list(
        session: AsyncSession, cache: Redis, current_user: User,
        collections: List[Collection], collections_count: int):
    """Executes after a collection list is retrieved."""
    ...


async def after_document_upload(
        session: AsyncSession, cache: Redis, current_user: User,
        document: Document):
    """Executes after a document is uploaded."""
    ...


async def after_document_select(
        session: AsyncSession, cache: Redis, current_user: User,
        document: Document):
    """Executes after a document is retrieved."""
    ...


async def after_document_update(
        session: AsyncSession, cache: Redis, current_user: User,
        document: Document):
    """Executes after a document is updated."""
    ...


async def after_document_move(
        session: AsyncSession, cache: Redis, current_user: User,
        document: Document):
    """Executes after a document is moved."""
    ...


async def after_document_delete(
        session: AsyncSession, cache: Redis, current_user: User,
        document: Document):
    """Executes after a document is deleted."""
    ...


async def after_document_list(
        session: AsyncSession, cache: Redis, current_user: User,
        documents: List[Document], documents_count: int):
    """Executes after a document list is retrieved."""
    ...


async def after_tag_insert(
        session: AsyncSession, cache: Redis, current_user: User,
        document: Document, tag: Tag):
    """Executes after a tag is created."""
    ...


async def after_tag_delete(
        session: AsyncSession, cache: Redis, current_user: User,
        document: Document, tag: Tag):
    """Executes after a tag is deleted."""
    ...


async def after_tag_list(
        session: AsyncSession, cache: Redis, current_user: User,
        tags: List[str]):
    """Executes after a tag list is retrieved."""
    ...


async def after_setting_insert(
        session: AsyncSession, cache: Redis, current_user: User,
        setting: Setting):
    """Executes after a setting is created."""
    ...


async def after_setting_list(
        session: AsyncSession, cache: Redis, current_user: User,
        settings: List[Setting]):
    """Executes after a setting list is retrieved."""
    ...


async def after_secret_retrieve(
        session: AsyncSession, cache: Redis, current_user: User,
        secret_key: str, secret_path: str, created_date: int):
    """Executes after a secret key is retrieved."""
    ...


async def after_secret_delete(
        session: AsyncSession, cache: Redis, current_user: User,
        secret_path: str):
    """Executes after a secret key is deleted."""
    ...


async def after_lock_create(
        session: AsyncSession, cache: Redis, current_user: User):
    """Executes after a lock is created."""
    ...


async def after_lock_retrieve(
        session: AsyncSession, cache: Redis, current_user: User,
        lock_exists: bool):
    """Executes after a lock is retrieved."""
    ...


async def after_telemetry_retrieve(
        session: AsyncSession, cache: Redis, current_user: User,
        telemetry: dict):
    """Executes after telemetry is retrieved."""
    ...


async def on_execute(
        session: AsyncSession, cache: Redis,
        current_user: User, action: str, params: dict, response: dict):
    """Executes when custom action is triggered."""
    ...
