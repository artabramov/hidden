import os
import uuid
from fastapi import APIRouter, Depends, Path, status, File, UploadFile, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.document_revision import DocumentRevision
from app.models.document_thumbnail import DocumentThumbnail
from app.models.collection import Collection
from app.validators.file_validators import name_validate
from app.hook import Hook, HOOK_AFTER_DOCUMENT_UPLOAD
from app.auth import auth
from app.repository import Repository
from app.schemas.document_upload import DocumentUploadResponse
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_FILE_WRITE_ERROR,
    ERR_VALUE_INVALID, ERR_FILE_MIMETYPE_INVALID, ERR_FILE_HASH_EXISTS)
from app.helpers.image_helper import (
    image_resize, IMAGE_MIMETYPES, IMAGE_EXTENSION)

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

    Files are stored under the collection directory; revisions and
    thumbnails are stored under their dedicated roots. The database
    enforces uniqueness of (collection_id, filename) for documents and
    (document_id, revision) for revisions.

    **Authentication:**
    - Requires a valid bearer token with `writer` role or higher.

    **Validation schemas:**
    - `DocumentUploadResponse` — contains the newly created document ID.

    **Path parameters:**
    - `collection_id` (integer) — target collection identifier.

    **Request body:**
    - `file` — the file to upload (`multipart/form-data`).

    **Response codes:**
    - `201` — file created or replaced (revision recorded when replaced).
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection not found.
    - `422` — invalid file name or write error.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_UPLOAD`: executed after a successful upload.
    """
    config = request.app.state.config
    log = request.state.log
    file_manager = request.app.state.file_manager

    # Temporary file after upload
    temporary_filename = str(uuid.uuid4()) + ".tmp"
    temporary_path = os.path.join(config.TEMPORARY_DIR, temporary_filename)

    # Revision file
    revision_path = None

    # File thumbnail
    thumbnail_path = None

    # Checking the correctness of the collection
    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # Checking the correctness of the file name
    try:
        document_filename = name_validate(file.filename)
    except ValueError:
        raise E([LOC_BODY, "file"], file.filename, ERR_VALUE_INVALID,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Perform operations using file lock
    file_lock_key = (collection_id, document_filename)
    file_lock = request.app.state.file_locks[file_lock_key]
    async with file_lock:

        # Look for a document with this name in the collection
        document_repository = Repository(session, cache, Document, config)
        document = await document_repository.select(
            filename__eq=document_filename, collection_id__eq=collection_id)

        # Look for a file with this name in the directory
        file_path = os.path.join(
            config.DOCUMENTS_DIR, collection.name, document_filename)
        file_exists = await file_manager.isfile(file_path)

        # Inconsistent state: document exists but file does not
        if document and not file_exists:
            raise E([LOC_BODY, "file"], file.filename, ERR_FILE_WRITE_ERROR,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Inconsistent state: document does not exist, but file exists
        elif not document and file_exists:
            raise E([LOC_BODY, "file"], file.filename, ERR_FILE_WRITE_ERROR,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)

        # Create a new document
        elif not document and not file_exists:
            file_renamed = False
            try:
                await file_manager.upload(file, temporary_path)
            except Exception as e:
                log.exception("file upload error; filename=%s;", file.filename)

                raise E(
                    [LOC_BODY, "file"], file.filename, ERR_FILE_WRITE_ERROR,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)

            try:
                document_filesize = await file_manager.filesize(temporary_path)
                document_mimetype = await file_manager.mimetype(temporary_path)
                document_checksum = await file_manager.checksum(temporary_path)
                document = Document(
                    current_user.id, collection.id, document_filename,
                    document_filesize, mimetype=document_mimetype,
                    checksum=document_checksum)

                await document_repository.insert(document, commit=False)
                await file_manager.rename(temporary_path, file_path)
                file_renamed = True
                await document_repository.commit()

            except Exception as e:
                log.exception("file rename error; filename=%s;", file.filename)

                try:
                    if file_renamed:
                        await file_manager.delete(file_path)
                    else:
                        await file_manager.delete(temporary_path)
                except Exception:
                    pass

                raise E([LOC_BODY, "file"], file.filename,
                        ERR_FILE_WRITE_ERROR,
                        status.HTTP_422_UNPROCESSABLE_ENTITY)

        # Update existing document (with revision)
        elif document and file_exists:

            # Upload the current file under a temporary filename
            try:
                await file_manager.upload(file, temporary_path)
            except Exception as e:
                log.exception("file upload error; filename=%s;", file.filename)

                raise E([LOC_BODY, "file"], file.filename,
                        ERR_FILE_WRITE_ERROR,
                        status.HTTP_422_UNPROCESSABLE_ENTITY)

            # MIME type of an existing file must not be changed
            file_mimetype = await file_manager.mimetype(temporary_path)
            if document.mimetype != file_mimetype:
                try:
                    await file_manager.delete(temporary_path)
                except Exception:
                    pass

                raise E([
                    LOC_BODY, "file"], file.filename,
                    ERR_FILE_MIMETYPE_INVALID,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)

            # If the file has not changed, then it does not need to be updated
            file_checksum = await file_manager.checksum(temporary_path)
            if document.checksum == file_checksum:
                try:
                    await file_manager.delete(temporary_path)
                except Exception:
                    pass

                raise E([
                    LOC_BODY, "file"], file.filename, ERR_FILE_HASH_EXISTS,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Copy outdated file to revision
            revision_uuid = str(uuid.uuid4())
            revision_path = os.path.join(config.REVISIONS_DIR, revision_uuid)

            try:
                await file_manager.copy(file_path, revision_path)
            except Exception as e:
                log.exception("file copy error; filename=%s;", file.filename)

                await file_manager.delete(temporary_path)
                raise E(
                    [LOC_BODY, "file"], file.filename, ERR_FILE_WRITE_ERROR,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Outdated thumbnail will be removed after commit
            if document.document_thumbnail is not None:
                thumbnail_path = os.path.join(
                    config.THUMBNAILS_DIR,
                    document.document_thumbnail.uuid)

            revision_repository = Repository(
                session, cache, DocumentRevision, config)
            
            file_replaced = False
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
                document.filesize = await file_manager.filesize(temporary_path)
                await document_repository.update(document, commit=False)

                # Atomic replacement of the file and commit
                await file_manager.rename(temporary_path, file_path)
                file_replaced = True
                await document_repository.commit()

            # Rollback everything if something goes wrong
            except Exception as e:
                log.exception("file rename error; filename=%s;", file.filename)

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

                raise E(
                    [LOC_BODY, "file"], file.filename, ERR_FILE_WRITE_ERROR,
                    status.HTTP_422_UNPROCESSABLE_ENTITY)

        # Remove outdated thumbnail
        if thumbnail_path:
            try:
                await file_manager.delete(thumbnail_path)
            except Exception:
                pass

        # Create a new thumbnail
        if document.mimetype in IMAGE_MIMETYPES:
            thumbnail_uuid = str(uuid.uuid4()) + IMAGE_EXTENSION
            thumbnail_path = os.path.join(config.THUMBNAILS_DIR, thumbnail_uuid)  # noqa E501

            try:
                await file_manager.copy(file_path, thumbnail_path)
                await image_resize(
                    thumbnail_path, config.THUMBNAILS_WIDTH,
                    config.THUMBNAILS_HEIGHT, config.THUMBNAILS_QUALITY)

                thumbnail_filesize = await file_manager.filesize(thumbnail_path)  # noqa E501
                thumbnail_checksum = await file_manager.checksum(thumbnail_path)  # noqa E501

                thumbnail_repository = Repository(
                    session, cache, DocumentThumbnail, config)
                
                thumbnail = DocumentThumbnail(
                    document.id, thumbnail_uuid, thumbnail_filesize,
                    thumbnail_checksum)
                
                await thumbnail_repository.insert(thumbnail)

            except Exception:
                await file_manager.delete(thumbnail_path)

    # Execute hooks
    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_UPLOAD, document)

    log.debug("file uploaded; filename=%s;", file.filename)
    return {
        "document_id": document.id,
        "latest_revision_number": document.latest_revision_number,
    }
