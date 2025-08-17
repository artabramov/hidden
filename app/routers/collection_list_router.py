from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_list_schema import (
    CollectionListRequest, CollectionListResponse)
from app.repository import Repository
from app.hook import Hook, HOOK_AFTER_COLLECTION_LIST
from app.auth import auth

router = APIRouter()


@router.get("/collections", summary="Retrieve a list of collections.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionListResponse, tags=["Collections"])
async def collection_list(
    request: Request, schema=Depends(CollectionListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> CollectionListResponse:
    """
    Retrieves a list of collections. Fetches collections from the
    repository based on the provided filter criteria, and includes
    a counter field to indicate the total number of matching
    collections.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `CollectionListResponse`: Contains the list of collections and the
    total count.

    **Responses:**
    - `200 OK`: If the collections are successfully fetched.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_LIST`: Executes after the collections are
    successfully fetched.
    """
    collection_repository = Repository(session, cache, Collection)

    collections = await collection_repository.select_all(**schema.__dict__)
    collections_count = await collection_repository.count_all(
        **schema.__dict__)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_LIST, collections, collections_count)

    return {
        "collections": [
            await collection.to_dict() for collection in collections],
        "collections_count": collections_count,
    }
