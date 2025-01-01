from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_schemas import (
    CollectionListRequest, CollectionListResponse)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import HOOK_AFTER_COLLECTION_LIST

router = APIRouter()


@router.get("/collections", summary="Retrieve a list of collections.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionListResponse, tags=["Collections"])
@locked
async def collection_list(
    schema=Depends(CollectionListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> CollectionListResponse:
    """
    Retrieve a list of collections. This endpoint fetches all
    collections from the repository based on the provided filter
    criteria and executes related hooks. The current user must have
    a reader role or higher. Returns a 200 response on success, a 401
    error if authentication failed or the user does not have the
    required permissions, a 403 error if the token is missing, a 422
    error if arguments validation failed, and a 423 error if the
    application is locked.

    **Args:**
    - `CollectionListRequest`: The request schema containing filter and
    pagination details.

    **Returns:**
    - `CollectionListResponse`: The response schema containing the list
    of collections and the total count.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `422 Unprocessable Entity`:  Raised if arguments validation failed.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_LIST`: Executes after the collections are
    retrieved.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `reader`, `writer`, `editor`, `admin` user role is required to
    access this router.
    """
    collection_repository = Repository(session, cache, Collection)

    collections = await collection_repository.select_all(**schema.__dict__)
    collections_count = await collection_repository.count_all(
        **schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_COLLECTION_LIST, collections)

    return {
        "collections": [
            await collection.to_dict() for collection in collections],
        "collections_count": collections_count,
    }
