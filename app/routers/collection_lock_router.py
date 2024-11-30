from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_schemas import (
    CollectionLockUpdateRequest, CollectionLockUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_COLLECTION_UPDATE,
    HOOK_AFTER_COLLECTION_UPDATE)

router = APIRouter()


@router.put("/collection/{collection_id}/locked",
            summary="Change collection locking.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionLockUpdateResponse, tags=["Collections"])
@locked
async def collection_delete(
    collection_id: int, schema: CollectionLockUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> CollectionLockUpdateResponse:
    collection_repository = Repository(session, cache, Collection)

    collection = await collection_repository.select(id=collection_id)
    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    collection.is_locked = schema.is_locked
    await collection_repository.update(collection, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COLLECTION_UPDATE, collection)

    await collection_repository.commit()
    await hook.do(HOOK_AFTER_COLLECTION_UPDATE, collection)

    return {"collection_id": collection.id}
