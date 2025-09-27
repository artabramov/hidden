"""FastAPI router for document deleting."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.document_delete import DocumentDeleteResponse
from app.hook import Hook, HOOK_AFTER_DOCUMENT_DELETE
from app.auth import auth
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_FILE_CONFLICT

router = APIRouter()


@router.delete(
    "/collection/{collection_id}/document/{document_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=DocumentDeleteResponse,
    summary="Delete document",
    tags=["Documents"]
)
async def document_delete(
    request: Request,
    collection_id: int = Path(..., ge=1),
    document_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DocumentDeleteResponse:
    """
    Delete a document and all associated artifacts (thumbnail,
    revisions, head file).

    **Authentication:**
    - Requires a valid bearer token with `admin` role.

    **Path parameters:**
    - `collection_id` (integer ≥ 1): parent collection identifier.
    - `document_id` (integer ≥ 1): document identifier.

    **Response:**
    - `DocumentDeleteResponse` with document ID and latest revision
    number.

    **Response codes:**
    - `200` — document deleted successfully.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or document not found.
    - `409` — conflict: thumbnail, revision or head file is missing.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Side effects:**
    - Deletes thumbnail, all revisions, and the head file from the
    filesystem; purges LRU cache entries.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_DELETE` — executed after successful deletion.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    collection_locks = request.app.state.collection_locks
    file_locks = request.app.state.file_locks

    # NOTE: On document delete, keep two-step fetch to hit Redis cache;
    # load the collection by ID first, then load the document by ID.

    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    document_repository = Repository(session, cache, Document, config)
    document = await document_repository.select(id=document_id)

    if not document or document.collection_id != collection.id:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    latest_revision_number = document.latest_revision_number

    # NOTE: On document delete, acquire the collection READ lock first,
    # then the per-file exclusive lock.

    collection_lock = collection_locks[collection_id]
    file_lock_key = (collection_id, document.filename)
    file_lock = file_locks[file_lock_key]
    async with collection_lock.read(), file_lock:

        # NOTE: On document delete the operation order is intentional:
        # (1) remove thumbnail, (2) remove revisions, (3) delete head.
        # The head is kept until the end to minimize the inconsistency
        # window. If filesystem operations fail, they likely fail at
        # step (1), so we fail early with minimal side effects. If any
        # step fails, the deletion is aborted entirely (no head removal).

        # Ensure the thumbnail file exists
        if document.has_thumbnail:
            thumbnail_path = document.document_thumbnail.path(config)
            thumbnail_file_exists = await file_manager.isfile(thumbnail_path)
            if not thumbnail_file_exists:
                raise E([LOC_PATH, "document_id"], document_id,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            await file_manager.delete(thumbnail_path)
            lru.delete(thumbnail_path)

        # Ensure the revision file exists
        if document.has_revisions:
            for revision in document.document_revisions:
                revision_path = revision.path(config)
                revision_file_exists = await file_manager.isfile(revision_path)
                if not revision_file_exists:
                    raise E([LOC_PATH, "document_id"], document_id,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                await file_manager.delete(revision_path)
                lru.delete(revision_path)

        # Ensure the head file exists
        document_path = document.path(config)
        current_file_exists = await file_manager.isfile(document_path)
        if not current_file_exists:
            raise E([LOC_PATH, "document_id"], document_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        await file_manager.delete(document_path)
        lru.delete(document_path)

        # NOTE: On document delete, all related DB entities
        # are removed by SQLAlchemy using ORM relationships.

        await document_repository.delete(document)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_DELETE, document_id)

    return {
        "document_id": document_id,
        "latest_revision_number": latest_revision_number,
    }
