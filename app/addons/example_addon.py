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
from app.models.document import Document


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


async def after_collection_select(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, collection: Collection):
    """Executes after a collection is retrieved."""
    ...


async def after_collection_update(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, collection: Collection):
    """Executes after a collection is updated."""
    ...


async def after_collection_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, collection_id: int):
    """Executes after a collection is deleted."""
    ...


async def after_collection_list(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, collections: List[Collection],
        collections_count: int):
    """Executes after a collection list is retrieved."""
    ...


async def after_document_upload(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document: Document):
    """Executes after a document is uploaded."""
    ...


async def after_document_download(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document: Document, revision_number: int):
    """Executes after a document is downloaded."""
    ...


async def after_document_select(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document: Document):
    """Executes after a document is retrieved."""
    ...


async def after_document_update(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document: Document):
    """Executes after a document is updated."""
    ...


async def after_document_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document_id: int):
    """Executes after a document is deleted."""
    ...


async def after_document_list(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, documents: List[Document], documents_count: int):
    """Executes after a document list is retrieved."""
    ...


async def after_thumbnail_retrieve(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document: Document):
    """Executes after a document thumbnail is retrieved."""
    ...


async def after_tag_insert(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document: Document, tag_value: str):
    """Executes after a document tag is added."""
    ...


async def after_tag_delete(
        request: Request, session: AsyncSession, cache: Redis,
        current_user: User, document: Document, tag_value: str):
    """Executes after a tag is deleted."""
    ...
