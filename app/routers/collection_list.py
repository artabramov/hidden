"""FastAPI router for collection listing."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.schemas.collection_list import (
    CollectionListRequest, CollectionListResponse)
from app.hook import Hook, HOOK_AFTER_COLLECTION_LIST
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get(
    "/collections",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=CollectionListResponse,
    summary="Retrieve list of collections",
    tags=["Collections"]
)
async def collection_list(
    request: Request,
    schema=Depends(CollectionListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> CollectionListResponse:
    """
    Retrieve collections matching the provided filters and return them
    with the total number of matches.

    **Authentication**
    - Requires a valid bearer token with `reader` role or higher.

    **Query parameters**
    - `CollectionListRequest` — optional filters (creation time, creator,
    readonly flag, name), pagination (offset/limit), and ordering
    (order_by/order).

    **Response**
    - `CollectionListResponse` — page of collections and total match
    count.

    **Response codes**
    - `200` — collection list returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks**
    - `HOOK_AFTER_COLLECTION_LIST` — executed after successful retrieval.
    """
    config = request.app.state.config
    kwargs = schema.model_dump(exclude_none=True)

    collection_repository = Repository(session, cache, Collection, config)
    collections = await collection_repository.select_all(**kwargs)
    collections_count = await collection_repository.count_all(**kwargs)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_LIST, collections, collections_count)

    return {
        "collections": [await c.to_dict() for c in collections],
        "collections_count": collections_count,
    }
