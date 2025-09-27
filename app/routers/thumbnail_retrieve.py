"""FastAPI router for thumbnail retrieving."""

from fastapi import APIRouter, Depends, status, Response, Request, Path
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_FILE_CONFLICT
from app.helpers.image_helper import IMAGE_MEDIATYPE
from app.hook import Hook, HOOK_AFTER_THUMBNAIL_RETRIEVE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get(
    "/collection/{collection_id}/document/{document_id}/thumbnail",
    status_code=status.HTTP_200_OK,
    response_class=Response,
    summary="Retrieve thumbnail",
    tags=["Documents"]
)
async def thumbnail_retrieve(
    request: Request,
    collection_id: int = Path(..., ge=1),
    document_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
):
    """
    Retrieve a document's thumbnail and return raw image bytes. The
    image is fetched from the LRU cache first; on miss, it is read from
    the filesystem, verified against the stored checksum, and cached.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Path parameters:**
    - `collection_id` (integer ≥ 1): parent collection identifier.
    - `document_id` (integer ≥ 1): document identifier.

    **Response:**
    - Raw binary image.

    **Response codes:**
    - `200` — thumbnail returned.
    - `304` — not modified (ETag matched).
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
      suspended.
    - `404` — collection or document not found, or no thumbnail set.
    - `409` — file not found on filesystem or checksum mismatch.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Side effects:**
    - Reads from the LRU cache or filesystem and saves the bytes into
    the LRU cache on cache miss.

    **Hooks:**
    - `HOOK_AFTER_THUMBNAIL_RETRIEVE`: executed after successful
    thumbnail retrieval.
    """

    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    # NOTE: On thumbnail retrieval, keep two-step fetch to hit Redis
    # cache; load the collection by ID first, then load the document
    # by ID.

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

    elif not document.has_thumbnail:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # NOTE: On thumbnail retrieval, if the file checksum is unchanged,
    # return a 304 response to skip further LRU/filesystem operations.

    etag = f'"{document.document_thumbnail.checksum}"'
    if request.headers.get("if-none-match") == etag:
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED,
            headers={"ETag": etag})

    file_path = document.document_thumbnail.path(config)
    file_data = lru.load(file_path)

    if file_data is None:

        # Ensure the thumbnail file exists
        file_exists = await file_manager.isfile(file_path)
        if not file_exists:
            raise E([LOC_PATH, "document_id"], document_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        # Ensure the file checksum is correct
        file_checksum = await file_manager.checksum(file_path)
        if document.document_thumbnail.checksum != file_checksum:
            raise E([LOC_PATH, "document_id"], document_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        file_data = await file_manager.read(file_path)
        lru.save(file_path, file_data)

    headers = {
        "ETag": etag,
        "Content-Disposition": "inline",
        "Content-Length": str(document.document_thumbnail.filesize),
    }

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_THUMBNAIL_RETRIEVE, document)

    return Response(
        content=file_data, media_type=IMAGE_MEDIATYPE, headers=headers)
