"""FastAPI router for file uploading."""

import os
import uuid
from fastapi import APIRouter, UploadFile, Request, Depends, Path, File, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.document_revision import DocumentRevision
from app.models.document_thumbnail import DocumentThumbnail
from app.models.collection import Collection
from app.schemas.document_upload import DocumentUploadResponse
from app.helpers.image_helper import image_resize, IMAGE_MIMETYPES
from app.validators.file_validators import name_validate
from app.repository import Repository
from app.hook import Hook, HOOK_AFTER_DOCUMENT_UPLOAD
from app.auth import auth
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_FILE_MIMETYPE_INVALID,
    ERR_VALUE_INVALID, ERR_FILE_CONFLICT)

router = APIRouter()


@router.post(
    "/collection/{collection_id}/document",
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=DocumentUploadResponse,
    summary="Upload file",
    tags=["Documents"]
)
async def document_upload(
    request: Request,
    collection_id: int = Path(..., ge=1),
    file: UploadFile = File(...),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> DocumentUploadResponse:
    """
    Uploads a file into the target collection. If no document with that
    name exists, a new one is created; if it does, the current head file
    is snapshotted as a new immutable revision and the upload becomes
    the new head. File metadata (size, MIME type, checksum) is computed
    from the uploaded content and persisted. Disk writes are performed
    via a temporary file followed by an atomic rename to avoid partial
    states.

    This operation is serialized per (collection_id, filename) using an
    in-process asyncio lock, so concurrent uploads of the same name in a
    single process are executed one by one. In the update path, if the
    database commit fails after the head file was already replaced on
    disk, the previous head is restored from the just-created revision
    to keep the filesystem and database consistent. Thumbnails are
    regenerated for image types inside the same critical section after
    a successful commit; any outdated thumbnail is removed first.

    **Authentication:**
    - Requires a valid bearer token with `writer` role or higher.

    **Validation schemas:**
    - `DocumentUploadResponse` — contains the newly created (or updated)
    document ID and the latest revision number.

    **Path parameters:**
    - `collection_id` (integer ≥ 1) — target collection identifier.

    **Request body:**
    - `file` — the file to upload (`multipart/form-data`).

    **Response codes:**
    - `201` — file successfully uploaded; document created or replaced
    (revision recorded when replaced); thumbnail generated or skipped.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role to perform the operation, invalid JTI,
    user is inactive or suspended.
    - `404` — collection not found.
    - `409` — conflict on DB/FS mismatch for the file (document present
    but file missing, or vice versa; MIME type changed for an existing
    file).
    - `422` — invalid file name.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_UPLOAD`: executed after a successful upload.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    collection_locks = request.app.state.collection_locks
    file_locks = request.app.state.file_locks

    temporary_filename = str(uuid.uuid4()) + ".tmp"
    temporary_path = os.path.join(config.TEMPORARY_DIR, temporary_filename)

    file_renamed = False
    file_replaced = False
    thumbnail_path = None

    try:
        filename = name_validate(file.filename)
    except ValueError:
        raise E([LOC_BODY, "file"], file.filename, ERR_VALUE_INVALID,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    # NOTE: On file upload, acquire the collection READ lock first,
    # then the per-file exclusive lock.

    collection_lock = collection_locks[collection_id]
    file_lock_key = (collection_id, filename)
    file_lock = file_locks[file_lock_key]
    async with collection_lock.read(), file_lock:

        # Ensure the collection exists
        collection_repository = Repository(session, cache, Collection, config)
        collection = await collection_repository.select(id=collection_id)
        if not collection:
            raise E([LOC_PATH, "collection_id"], collection_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        # Check the document with the filename in the collection
        document_repository = Repository(session, cache, Document, config)
        document = await document_repository.select(
            filename__eq=filename, collection_id__eq=collection_id)

        # Check the file with the filename in the directory
        file_path = Document.path_for_filename(
            config, collection.name, filename)
        file_exists = await file_manager.isfile(file_path)

        # Inconsistent state: document exists but file does not
        if document and not file_exists:
            raise E([LOC_BODY, "file"], file.filename,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)
        
        # Inconsistent state: file exists but document does not
        elif not document and file_exists:
            raise E([LOC_BODY, "file"], file.filename,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        # Create a new document
        elif not document and not file_exists:
            await file_manager.upload(file, temporary_path)

            try:
                filesize, mimetype, checksum = (
                    await file_manager.filesize(temporary_path),
                    await file_manager.mimetype(temporary_path),
                    await file_manager.checksum(temporary_path))

                document = Document(
                    current_user.id, collection.id, filename,
                    filesize, mimetype=mimetype, checksum=checksum)
                await document_repository.insert(document, commit=False)

                await file_manager.rename(temporary_path, file_path)
                file_renamed = True

                await document_repository.commit()
                lru.delete(file_path)

            except Exception:
                if file_renamed:
                    await file_manager.delete(file_path)
                else:
                    await file_manager.delete(temporary_path)
                raise

        # Update existing document and create revision
        elif document and file_exists:
            revision_path = None
            await file_manager.upload(file, temporary_path)

            # MIME type of an existing file must not be changed
            file_mimetype = await file_manager.mimetype(temporary_path)
            if document.mimetype != file_mimetype:
                await file_manager.delete(temporary_path)
                raise E([LOC_BODY, "file"], file.filename,
                        ERR_FILE_MIMETYPE_INVALID, status.HTTP_409_CONFLICT)

            # Check the file checksum
            try:
                file_checksum = await file_manager.checksum(temporary_path)
            except Exception:
                await file_manager.delete(temporary_path)
                raise
            
            # NOTE: File upload is idempotent: if file matches current
            # head (checksum), return successful response; skip DB/FS
            # changes, revision unchanged.

            if document.checksum != file_checksum:
                # Copy outdated file to revision
                revision_uuid = str(uuid.uuid4())
                revision_path = DocumentRevision.path_for_uuid(
                    config, revision_uuid)

                try:
                    await file_manager.copy(file_path, revision_path)
                except Exception:
                    await file_manager.delete(temporary_path)
                    raise

                # Outdated thumbnail will be removed after commit
                if document.has_thumbnail:
                    thumbnail_path = document.document_thumbnail.path(config)

                revision_repository = Repository(
                    session, cache, DocumentRevision, config)

                latest_revision_number = document.latest_revision_number + 1

                try:
                    # Create a new revision
                    revision = DocumentRevision(
                        current_user.id, document.id, latest_revision_number,
                        revision_uuid, document.filesize, document.checksum)
                    await revision_repository.insert(revision, commit=False)
                
                    # Update the document itself
                    document.latest_revision_number = latest_revision_number
                    document.document_thumbnail = None
                    document.checksum = file_checksum
                    document.filesize = await file_manager.filesize(
                        temporary_path)
                    await document_repository.update(document, commit=False)

                    # Atomic replacement of the file and commit
                    await file_manager.rename(temporary_path, file_path)
                    file_replaced = True

                    await document_repository.commit()
                    lru.delete(file_path)

                # Rollback if something goes wrong
                except Exception:
                    await document_repository.rollback()

                    try:
                        if file_replaced:
                            await file_manager.rename(revision_path, file_path)
                            revision_path = None
                        else:
                            await file_manager.delete(temporary_path)
                    except Exception:
                        pass

                    if revision_path:
                        try:
                            await file_manager.delete(revision_path)
                        except Exception:
                            pass

                    raise

            else:
                await file_manager.delete(temporary_path)

        # Remove the outdated thumbnail
        if thumbnail_path:
            try:
                await file_manager.delete(thumbnail_path)
                lru.delete(thumbnail_path)
            except Exception:
                pass

        # Create a new thumbnail
        if ((file_renamed or file_replaced) and
                document.mimetype in IMAGE_MIMETYPES):
            thumbnail_uuid = str(uuid.uuid4())
            thumbnail_path = DocumentThumbnail.path_for_uuid(
                config, thumbnail_uuid)

            try:
                await file_manager.copy(file_path, thumbnail_path)
                await image_resize(
                    thumbnail_path, config.THUMBNAILS_WIDTH,
                    config.THUMBNAILS_HEIGHT, config.THUMBNAILS_QUALITY)


                thumbnail_repository = Repository(
                    session, cache, DocumentThumbnail, config)
                
                thumbnail_filesize, thumbnail_checksum = (
                    await file_manager.filesize(thumbnail_path),
                    await file_manager.checksum(thumbnail_path))

                thumbnail = DocumentThumbnail(
                    document.id, thumbnail_uuid, thumbnail_filesize,
                    thumbnail_checksum)

                await thumbnail_repository.insert(thumbnail)

            except Exception:
                await file_manager.delete(thumbnail_path)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_UPLOAD, document)

    return {
        "document_id": document.id,
        "latest_revision_number": document.latest_revision_number,
    }
