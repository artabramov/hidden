"""FastAPI router for retrieving collection details by ID."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.schemas.collection_select import CollectionSelectResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_COLLECTION_SELECT
from app.auth import auth

router = APIRouter()


@router.get("/collection/{collection_id}", summary="Retrieve collection",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionSelectResponse, tags=["Collections"])
async def collection_select(
    request: Request, collection_id: int = Path(..., ge=1),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> CollectionSelectResponse:
    """
    Retrieve a single collection by ID and return its details, including
    creator info, creation and updateion timestamps, read-only flag,
    name, and optional summary.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Response schema:**
    - `CollectionSelectResponse` — includes collection ID; creator;
    creation and last-update timestamps (Unix seconds, UTC); read-only
    flag; normalized name; and optional summary.

    **Path parameters:**
    - `collection_id` (integer): identifier of the collection to
    retrieve.

    **Response codes:**
    - `200` — collection found; details returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection not found.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_SELECT`: executed after a successful
    retrieval.
    """

    config = request.app.state.config

    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_SELECT, collection)

    request.state.log.debug(
        "collection selected; collection_id=%s;", collection.id)
    return await collection.to_dict()
