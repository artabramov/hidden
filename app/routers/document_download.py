"""FastAPI router for file downloading."""

from fastapi import APIRouter, Request, Response, Path, Depends, status
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_FILE_CONFLICT
from app.auth import auth
from app.hook import Hook, HOOK_AFTER_DOCUMENT_DOWNLOAD
from app.repository import Repository

router = APIRouter()


@router.get(
    "/collection/{collection_id}/document/{document_id}/revision/{revision_number}",  # noqa E501
    status_code=status.HTTP_200_OK,
    response_class=Response,
    summary="Download file",
    tags=["Documents"]
)
async def document_download(
    request: Request,
    collection_id: int = Path(..., ge=1),
    document_id: int = Path(..., ge=1),
    revision_number: int = Path(..., ge=0),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    """
    Download a document file (current head or a specific revision)
    within a given collection. Returns the raw file bytes with the
    document's MIME type, and the original filename.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Path parameters:**
    - `collection_id` (integer ≥ 1): parent collection identifier.
    - `document_id` (integer ≥ 1): document identifier.
    - `revision_number` (integer ≥ 0): 0 for the current file head;
    > 0 for a specific revision.

    **Response codes:**
    - `200` — file returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection, document, or revision not found.
    - `409` — file not found on filesystem or checksum mismatch.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_DOWNLOAD` — executed after a successful read.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    # NOTE: On file download, keep two-step fetch to hit Redis cache;
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

    # NOTE: On file download, checksum verification is applied to
    # prevent replacement with a fake (both head and revisions).

    if revision_number == 0:
        file_path = document.path(config)
        checksum = document.checksum
        filesize = document.filesize

    else:
        revision = next((r for r in document.document_revisions
                        if r.revision_number == revision_number), None)

        if not revision:
            raise E([LOC_PATH, "document_id"], document_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        file_path = revision.path(config)
        checksum = revision.checksum
        filesize = revision.filesize

    file_data = lru.load(file_path)
    if file_data is None:

        # Ensure the file exists
        file_exists = await file_manager.isfile(file_path)
        if not file_exists:
            raise E([LOC_PATH, "document_id"], document_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        # Ensure the file checksum is correct
        file_checksum = await file_manager.checksum(file_path)
        if checksum != file_checksum:
            raise E([LOC_PATH, "document_id"], document_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        file_data = await file_manager.read(file_path)
        lru.save(file_path, file_data)

    headers = {
        "Content-Disposition": f'attachment; filename="{document.filename}"',
        "Content-Length": str(filesize),
        "Cache-Control": "no-store",
    }

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_DOWNLOAD, document, revision_number)

    return Response(
        content=file_data, media_type=document.mimetype, headers=headers)
