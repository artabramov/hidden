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


@router.get("/collections", summary="Retrieve collection list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionListResponse, tags=["Collections"])
@locked
async def collection_list(
    schema=Depends(CollectionListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> CollectionListResponse:
    """
    FastAPI router for retrieving a list of collection entities. The
    router fetches the list of collections from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
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
