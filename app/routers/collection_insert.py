"""FastAPI router for creating collections."""

import os
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.collection import Collection
from app.models.user import User, UserRole
from app.repository import Repository
from app.schemas.collection_insert import (
    CollectionInsertRequest, CollectionInsertResponse)
from app.hook import Hook, HOOK_AFTER_COLLECTION_INSERT
from app.error import E, LOC_BODY, ERR_VALUE_EXISTS
from app.auth import auth

router = APIRouter()


@router.post("/collection", summary="Create new collection.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=CollectionInsertResponse, tags=["Collections"])
async def collection_insert(
    request: Request, schema: CollectionInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> CollectionInsertResponse:
    """
    Create a new collection and a matching directory on the filesystem,
    then return the ID. The collection name must be unique; if a name
    is already taken, the request is rejected.

    **Authentication:**
    - Requires a valid bearer token with `writer` role or higher.

    **Validation schemas:**
    - `CollectionInsertRequest` — request body with read-only flag,
    name, and optional summary.
    - `CollectionInsertResponse` — contains the newly created
    collection ID.

    **Request body:**
    - `readonly` (boolean): read-only flag for the collection.
    - `name` (string, 1-256; ≤255 UTF-8 bytes): collection name;
    trimmed; `/` and NUL are not allowed.
    - `summary` (string, 0-4096): optional description; trimmed; empty
    becomes NULL.

    **Response codes:**
    - `201` — collection successfully created.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `422` — name already exists or fails validation.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Side effects:**
    - Creates a directory at `documents/<name>`.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_INSERT`: executed after collection and
    directory are successfully created.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    collection_repository = Repository(session, cache, Collection, config)

    collection_exists = await collection_repository.exists(
        name__eq=schema.name)

    if collection_exists:
        raise E([LOC_BODY, "name"], schema.name,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    collection_path = os.path.join(config.DOCUMENTS_DIR, schema.name)
    await file_manager.mkdir(collection_path)

    collection = Collection(
        current_user.id, schema.readonly, schema.name, summary=schema.summary)
    await collection_repository.insert(collection)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_INSERT, collection)

    request.state.log.debug(
        "collection created; collection_id=%s;", collection.id)
    return {"collection_id": collection.id}
