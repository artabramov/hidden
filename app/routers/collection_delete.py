"""FastAPI router for collection deleting."""

from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.collection_delete import CollectionDeleteResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_COLLECTION_DELETE
from app.auth import auth

router = APIRouter()


@router.delete(
    "/collection/{collection_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=CollectionDeleteResponse,
    summary="Delete collection",
    tags=["Collections"]
)
async def collection_delete(
    request: Request,
    collection_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> CollectionDeleteResponse:
    """
    Delete a collection and all its documents (including thumbnails,
    revisions, and head files).

    Disk cleanup is best-effort: missing thumbnails/revisions/head
    files are ignored. A WRITE lock on the collection is taken to
    block concurrent file operations during deletion.

    **Authentication:**
    - Requires a valid bearer token with `admin` role.

    **Path parameters:**
    - `collection_id` (integer ≥ 1): collection identifier.

    **Response:**
    - `CollectionDeleteResponse` — returns the deleted collection ID.

    **Response codes:**
    - `200` — collection deleted.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection not found.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Side effects:**
    - Removes thumbnails, revisions, and head files from the filesystem
    (best-effort); purges LRU cache entries.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_DELETE` — executed after successful
    deletion.
    """
    config = request.app.state.config
    lru = request.app.state.lru
    file_manager = request.app.state.file_manager
    collection_locks = request.app.state.collection_locks

    # Ensure the collection exists
    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # NOTE: On collection delete, acquire the collection WRITE lock
    # to block any file operations inside.

    collection_lock = collection_locks[collection.id]
    async with collection_lock.write():

        # TODO: Switch to batched deletion (fixed-size chunks) to reduce
        # lock time and memory usage spikes during collection removal.

        document_repository = Repository(session, cache, Document, config)
        documents = await document_repository.select_all(
            collection_id__eq=collection.id)

        # NOTE: On collection delete, missing thumbnails/revisions/head
        # files are ignored; deletion proceeds without conflict errors
        # (best-effort cleanup).

        for document in documents:

            # Remove the thumbnail file; no error if absent
            if document.has_thumbnail:
                thumbnail_path = document.document_thumbnail.path(config)
                await file_manager.delete(thumbnail_path)
                lru.delete(thumbnail_path)

            # Remove the revision files; no error if absent
            if document.has_revisions:
                for revision in document.document_revisions:
                    revision_path = revision.path(config)
                    await file_manager.delete(revision_path)
                    lru.delete(revision_path)

            # Remove the head file; no error if absent
            document_path = document.path(config)
            await file_manager.delete(document_path)
            lru.delete(document_path)

            # NOTE: On document delete, all related DB entities
            # are removed by SQLAlchemy using ORM relationships.

            await document_repository.delete(document)

        await collection_repository.delete(collection)

        collection_path = collection.path(config)
        await file_manager.rmdir(collection_path)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_DELETE, collection_id)

    return {"collection_id": collection.id}
