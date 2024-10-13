"""
This module contains asynchronous functions that handle post-processing
actions for various entities, including user registrations, updates, and
logins; collection and document operations; comment management; download
tracking; and favorite interactions. Each function logs specific actions
performed on these entities, capturing details about the request,
current user, and the entity involved. The log entries are inserted into
the database for audit purposes, and the functions return the processed
entity or list of entities.
"""

import enum
import json
import time
from typing import List
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (Column, BigInteger, Integer, ForeignKey, Enum,
                        JSON, String)
from fastapi import Request
from app.database import Base
from app.models.user_model import User
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.comment_model import Comment
from app.models.download_model import Download
from app.models.favorite_model import Favorite
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager

LOG_AFTER_USER_REGISTER = True
LOG_AFTER_USER_LOGIN = True
LOG_AFTER_TOKEN_SELECT = True
LOG_AFTER_ERR_TOKEN_INVALIDATE = True
LOG_AFTER_USER_SELECT = True
LOG_AFTER_USER_UPDATE = True
LOG_AFTER_ROLE_UPDATE = True
LOG_AFTER_PASSWORD_UPDATE = True
LOG_AFTER_USERPIC_UPLOAD = True
LOG_AFTER_USERPIC_DELETE = True
LOG_AFTER_USER_LIST = False
LOG_AFTER_COLLECTION_INSERT = True
LOG_AFTER_COLLECTION_SELECT = True
LOG_AFTER_COLLECTION_UPDATE = True
LOG_AFTER_COLLECTION_DELETE = True
LOG_AFTER_COLLECTION_LIST = False
LOG_AFTER_DOCUMENT_UPLOAD = True
LOG_AFTER_DOCUMENT_SELECT = True
LOG_AFTER_COMMENT_INSERT = True
LOG_AFTER_COMMENT_SELECT = True
LOG_AFTER_COMMENT_UPDATE = True
LOG_AFTER_COMMENT_DELETE = True
LOG_AFTER_COMMENT_LIST = False
LOG_AFTER_DOWNLOAD_SELECT = True
LOG_AFTER_DOWNLOAD_LIST = True
LOG_AFTER_FAVORITE_INSERT = True
LOG_AFTER_FAVORITE_SELECT = True
LOG_AFTER_FAVORITE_DELETE = True
LOG_AFTER_FAVORITE_LIST = False

OBSCURED_KEYS = ["user_password", "current_password", "updated_password",
                 "user_totp", "password_hash", "mfa_secret_encrypted",
                 "jti_encrypted"]
OBSCURED_VALUE = "*" * 6


class RequestMethod(enum.Enum):
    """
    Enumeration for standard HTTP request methods: GET for retrieving
    data, POST for submitting data, PUT for updating or creating
    resources, and DELETE for removing resources.
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class LogAction(enum.Enum):
    """
    Enumeration for CRUD operations representing actions on entities:
    insert for adding new entities, select for retrieving entities,
    update for modifying existing entities, and delete for removing
    entities.
    """
    insert = "insert"
    select = "select"
    update = "update"
    delete = "delete"


class Log(Base):
    """
    Represents a log entry capturing details of operations on the
    application entities, including the request method, URL, request
    parameters, and the action performed on the entity. The log records
    the user who initiated the request and the state of the entity at
    the time of the operation.
    """
    __tablename__ = "users_logs"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    request_method = Column(Enum(RequestMethod), index=True)
    request_url = Column(String(256), index=True)
    request_params = Column(JSON)
    log_action = Column(Enum(LogAction), index=True)
    entity_tablename = Column(String(128), index=True)
    entity_id = Column(BigInteger, index=True)
    entity_dict = Column(JSON)

    def __init__(self, current_user: User, request: Request,
                 entity: DeclarativeBase, log_action: LogAction):
        """
        Initializes a Log instance with details of the request, entity,
        and action performed. It sets the user ID, request method, URL,
        request parameters, and entity information, including the action
        performed and the entity state at the time of the request.
        """
        self.user_id = current_user.id if current_user else None
        self.request_method = request.method
        self.request_url = request.url.path
        self.request_params = self._to_dict(request.query_params._dict)
        self.log_action = log_action
        self.entity_tablename = entity.__tablename__
        self.entity_id = entity.id
        self.entity_dict = self._to_dict(entity.__dict__)

    def _to_dict(self, entity_dict: dict) -> json:
        """
        Converts a dictionary of entity attributes into a dictionary of
        string representations, obscuring sensitive information based on
        predefined keys. This method filters out private attributes and
        returns a clean, readable representation of the entity's state.
        """
        return {x: repr(entity_dict[x])
                if x not in OBSCURED_KEYS else OBSCURED_VALUE
                for x in entity_dict if not x.startswith("_")}


async def after_user_register(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user registration event, capturing details about the
    new user and the request. Returns the registered user.
    """
    if LOG_AFTER_USER_REGISTER:
        log = Log(current_user, request, user, LogAction.insert)
        await entity_manager.insert(log)
    return user


async def after_user_login(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user login event, capturing details about the user
    and the request. Returns the logged-in user.
    """
    if LOG_AFTER_USER_LOGIN:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_token_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a token retrieval event, capturing details about the user
    and the request. Returns the user associated with the token.
    """
    if LOG_AFTER_TOKEN_SELECT:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_token_invalidate(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a token invalidation event, capturing details about the user
    and the request. Returns the user associated with the invalidated
    token.
    """
    if LOG_AFTER_ERR_TOKEN_INVALIDATE:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_user_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user selection event, capturing details about the user
    and the request. Returns the selected user.
    """
    if LOG_AFTER_USER_SELECT:
        log = Log(current_user, request, user, LogAction.select)
        await entity_manager.insert(log)
    return user


async def after_user_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user update event, capturing details about the user and
    the request. Returns the updated user.
    """
    if LOG_AFTER_USER_UPDATE:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_role_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user role update event, capturing details about the user and
    the request. Returns the user whose role was updated.
    """
    if LOG_AFTER_ROLE_UPDATE:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_password_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a password update event, capturing details about the user and
    the request. Returns the user whose password was updated.
    """
    if LOG_AFTER_PASSWORD_UPDATE:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_userpic_upload(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user picture upload event, capturing details about the user
    and the request. Returns the user whose picture was uploaded.
    """
    if LOG_AFTER_USERPIC_UPLOAD:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_userpic_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user picture deletion event, capturing details about the user
    and the request. Returns the user whose picture was deleted.
    """
    if LOG_AFTER_USERPIC_DELETE:
        log = Log(current_user, request, user, LogAction.update)
        await entity_manager.insert(log)
    return user


async def after_user_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    users: List[Collection]
) -> List[Collection]:
    """
    Logs a user list retrieval event for each user in the list,
    capturing details about each user and the request. Returns the
    list of users.
    """
    if LOG_AFTER_USER_LIST:
        for user in users:
            log = Log(current_user, request, user, LogAction.select)
            await entity_manager.insert(log)
    return users


async def after_collection_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection insertion event, capturing details about the
    collection and the request. Returns the newly inserted collection.
    """
    if LOG_AFTER_COLLECTION_INSERT:
        log = Log(current_user, request, collection, LogAction.insert)
        await entity_manager.insert(log)
    return collection


async def after_collection_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection selection event, capturing details about the
    collection and the request. Returns the selected collection.
    """
    if LOG_AFTER_COLLECTION_SELECT:
        log = Log(current_user, request, collection, LogAction.select)
        await entity_manager.insert(log)
    return collection


async def after_collection_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection update event, capturing details about the
    collection and the request. Returns the updated collection.
    """
    if LOG_AFTER_COLLECTION_UPDATE:
        log = Log(current_user, request, collection, LogAction.update)
        await entity_manager.insert(log)
    return collection


async def after_collection_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection deletion event, capturing details about the
    collection and the request. Returns the deleted collection.
    """
    if LOG_AFTER_COLLECTION_DELETE:
        log = Log(current_user, request, collection, LogAction.delete)
        await entity_manager.insert(log)
    return collection


async def after_collection_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collections: List[Collection]
) -> List[Collection]:
    """
    Logs a collections list retrieval event for each collection in the
    list, capturing details about each collection and the request.
    Returns the list of collections.
    """
    if LOG_AFTER_COLLECTION_LIST:
        for collection in collections:
            log = Log(current_user, request, collection, LogAction.select)
            await entity_manager.insert(log)
    return collections


async def after__insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Logs a document upload event, capturing details about the document
    and the request. Returns the uploaded document.
    """
    if LOG_AFTER_DOCUMENT_UPLOAD:
        log = Log(current_user, request, document, LogAction.insert)
        await entity_manager.insert(log)
    return document


async def after_document_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Logs a document selection event, capturing details about the
    document and the request. Returns the selected document.
    """
    if LOG_AFTER_DOCUMENT_SELECT:
        log = Log(current_user, request, document, LogAction.select)
        await entity_manager.insert(log)
    return document


async def after_comment_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment insertion event, capturing details about the comment
    and the request. Returns the inserted comment.
    """
    if LOG_AFTER_COMMENT_INSERT:
        log = Log(current_user, request, comment, LogAction.insert)
        await entity_manager.insert(log)
    return comment


async def after_comment_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment retrieval event, capturing details about the comment
    and the request. Returns the selected comment.
    """
    if LOG_AFTER_COMMENT_SELECT:
        log = Log(current_user, request, comment, LogAction.select)
        await entity_manager.insert(log)
    return comment


async def after_comment_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment update event, capturing details about the updated
    comment and the request. Returns the updated comment.
    """
    if LOG_AFTER_COMMENT_UPDATE:
        log = Log(current_user, request, comment, LogAction.update)
        await entity_manager.insert(log)
    return comment


async def after_comment_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment deletion event, capturing details about the deleted
    comment and the request. Returns the deleted comment.
    """
    if LOG_AFTER_COMMENT_DELETE:
        log = Log(current_user, request, comment, LogAction.delete)
        await entity_manager.insert(log)
    return comment


async def after_comment_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comments: List[Comment]
) -> List[Comment]:
    """
    Logs the retrieval of a list of comments, capturing details about
    each comment and the request. Returns the list of comments.
    """
    if LOG_AFTER_COMMENT_LIST:
        for comment in comments:
            log = Log(current_user, request, comment, LogAction.select)
            await entity_manager.insert(log)
    return comments


async def after_download_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    download: Download
) -> Download:
    """
    Logs the selection of a download event, capturing details about the
    download and the request. Returns the download record.
    """
    if LOG_AFTER_DOWNLOAD_SELECT:
        log = Log(current_user, request, download, LogAction.select)
        await entity_manager.insert(log)
    return download


async def after_download_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    downloads: List[Download]
) -> List[Download]:
    """
    Logs the retrieval of a list of downloads, capturing details about
    each download and the request. Returns the list of downloads.
    """
    if LOG_AFTER_DOWNLOAD_LIST:
        for download in downloads:
            log = Log(current_user, request, download, LogAction.select)
            await entity_manager.insert(log)
    return downloads


async def after_favorite_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs the addition of a new favorite, capturing details about the
    favorite and the request. Returns the newly added favorite.
    """
    if LOG_AFTER_FAVORITE_INSERT:
        log = Log(current_user, request, favorite, LogAction.insert)
        await entity_manager.insert(log)
    return favorite


async def after_favorite_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs the retrieval of a favorite, capturing details about the
    favorite and the request. Returns the favorite.
    """
    if LOG_AFTER_FAVORITE_SELECT:
        log = Log(current_user, request, favorite, LogAction.select)
        await entity_manager.insert(log)
    return favorite


async def after_favorite_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs the deletion of a favorite, capturing details about the
    favorite and the request. Returns the deleted favorite.
    """
    if LOG_AFTER_FAVORITE_DELETE:
        log = Log(current_user, request, favorite, LogAction.delete)
        await entity_manager.insert(log)
    return favorite


async def after_favorite_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorites: List[Favorite]
) -> List[Favorite]:
    """
    Logs the retrieval of a list of favorites, capturing details about
    each favorite and the request. Returns the list of retrieved
    favorites.
    """
    if LOG_AFTER_FAVORITE_LIST:
        for favorite in favorites:
            log = Log(current_user, request, favorite, LogAction.select)
            await entity_manager.insert(log)
    return favorites
