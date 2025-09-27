from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.schemas.collection_update import (
    CollectionUpdateRequest, CollectionUpdateResponse)
from app.repository import Repository
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_VALUE_EXISTS)
from app.hook import Hook, HOOK_AFTER_COLLECTION_UPDATE
from app.auth import auth

router = APIRouter()


@router.put(
    "/collection/{collection_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=CollectionUpdateResponse,
    summary="Update collection",
    tags=["Collections"]
)
async def collection_update(
    request: Request,
    schema: CollectionUpdateRequest,
    collection_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> CollectionUpdateResponse:

    config = request.app.state.config
    file_manager = request.app.state.file_manager
    log = request.state.log

    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # Does a collection with this name already exist?
    collection_exists = await collection_repository.exists(
        name__eq=schema.name, id__ne=collection.id)

    if collection_exists:
        raise E([LOC_BODY, "name"], schema.name,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    current_name = collection.name
    current_path = collection.path(config)

    updated_name = schema.name
    updated_path = Collection.path_for_dir(config, updated_name)

    # Exclusive lock on the collection
    collection_lock = request.app.state.collection_locks[collection.id]
    async with collection_lock.write():

        # No-op rename: only summary changes
        if updated_name == current_name:
            collection.summary = schema.summary
            await collection_repository.update(collection)

        else:
            # Does a directory with this name already exist?
            directory_exists = await file_manager.isdir(updated_path)
            if directory_exists:
                raise E([LOC_BODY, "name"], schema.name,
                        ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

            try:
                collection_renamed = False
                await file_manager.rename(current_path, updated_path)
                collection_renamed = True

                collection.name = schema.name
                collection.summary = schema.summary
                await collection_repository.update(collection)

            except Exception:
                if collection_renamed:
                    try:
                        await file_manager.rename(updated_path, current_path)

                    except Exception:
                        log.exception(
                            "collection rename failed; collection_id=%s;",
                            collection.id)

                # Rollback successful: raise original
                # error without losing stacktrace
                raise

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_UPDATE, collection)

    log.debug("collection updated; collection_id=%s;", collection.id)
    return {"collection_id": collection.id}
