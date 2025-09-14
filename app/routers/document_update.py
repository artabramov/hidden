import os
from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.document_update import (
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.hook import Hook, HOOK_AFTER_DOCUMENT_UPDATE
from app.auth import auth
from app.repository import Repository
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_VALUE_EXISTS,
    ERR_FILE_NOT_FOUND, ERR_FILE_EXISTS, ERR_FILE_WRITE_ERROR)

router = APIRouter()


@router.put(
    "/collection/{collection_id}/document/{document_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=DocumentUpdateResponse,
    summary="Update document",
    tags=["Documents"]
)
async def document_update(
    request: Request,
    schema: DocumentUpdateRequest,
    collection_id: int = Path(..., ge=1),
    document_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentUpdateResponse:
    """
    Updates a document by renaming its head file within the current
    collection, moving the head file to a different collection (keeping
    its name), and/or changing the document summary. Disk changes are
    performed with an atomic rename; the document row is staged
    (no-commit), the file is renamed or moved on disk, and then the
    transaction is committed to keep database and filesystem in sync.

    Concurrency is controlled with per-path locks. For rename/move, two
    locks are acquired in a deterministic order to prevent AB-BA
    deadlocks. All database and filesystem checks are executed inside
    this critical section. These locks are in-process.

    Files are stored under their collection directory. The database
    enforces uniqueness of (collection_id, filename) for documents.
    
    **Authentication:**
    - Requires a valid bearer token with `editor` role or higher.

    **Validation schemas:**
    - `DocumentUpdateRequest` — optional fields: `filename`, `summary`,
    `collection_id`.
    - `DocumentUpdateResponse` — returns `document_id` and
    `latest_revision_number`.

    **Path parameters:**
    - `collection_id` (integer) — current collection identifier.
    - `document_id` (integer) — document identifier.

    **Request body:**
    - `application/json` with any of: `filename`, `summary`,
    `collection_id`.

    **Response codes:**
    - `200` — update successful.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or document not found; source file missing on
    disk.
    - `422` — validation or write error: name conflict in DB; file
    conflict on filesystem; filesystem write/rename error.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_UPDATE` — executed after a successful update.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    log = request.state.log

    # NOTE: Select by ID hits Redis cache; keep two-step fetch:
    # load the collection by ID, then load the document by ID.
    # Do NOT combine into a single filtered query.

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

    document.summary = schema.summary
    document_updated = False

    # Rename the file if the filename changes
    if schema.filename is not None and document.filename != schema.filename:

        # NOTE: Acquire two per-path locks (source and target) in a
        # deterministic order to prevent AB-BA deadlocks. Do all checks
        # under these locks. These are per-process locks; for multiple
        # workers, a distributed lock is required (e.g. Redis).

        first_lock_key = (collection_id, document.filename)
        second_lock_key = (collection_id, schema.filename)

        first_lock_key, second_lock_key = sorted((
            first_lock_key, second_lock_key))

        first_file_lock = request.app.state.file_locks[first_lock_key]
        second_file_lock = request.app.state.file_locks[second_lock_key]

        async with first_file_lock, second_file_lock:

            # Is there a document with this filename in the collection?
            filename_exists = await document_repository.select(
                id__ne=document.id, filename__eq=schema.filename,
                collection_id__eq=collection.id)
            if filename_exists:
                raise E([LOC_BODY, "filename"], schema.filename,
                        ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Is there a file with current filename in the directory?
            current_file_path = os.path.join(
                config.DOCUMENTS_DIR, collection.name, document.filename)
            current_file_exists = await file_manager.isfile(current_file_path)
            if not current_file_exists:
                raise E([LOC_BODY, "filename"], document.filename,
                        ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

            # Is there a file with new filename in the directory?
            updated_file_path = os.path.join(
                config.DOCUMENTS_DIR, collection.name, schema.filename)
            updated_file_exists = await file_manager.isfile(updated_file_path)
            if updated_file_exists:
                raise E([LOC_BODY, "filename"], schema.filename,
                        ERR_FILE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

            try:
                document.filename = schema.filename
                await document_repository.update(document, commit=False)
                await file_manager.rename(current_file_path, updated_file_path)
                await document_repository.commit()
                document_updated = True

            except Exception:
                await document_repository.rollback()
                log.exception(
                    "file rename error; filename=%s;", schema.filename)
                raise E(
                    [LOC_BODY, "filename"], schema.filename,
                    ERR_FILE_WRITE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Move the file if collection changes
    if (schema.collection_id is not None
            and document.collection_id != schema.collection_id):

        # Does the target collection exist?
        target_collection = await collection_repository.select(
            id=schema.collection_id)
        if not target_collection:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        # NOTE: Acquire two per-path locks (source and target) in a
        # deterministic order to prevent AB-BA deadlocks. Do all checks
        # under these locks. These are per-process locks; for multiple
        # workers, a distributed lock is required (e.g. Redis).

        first_lock_key = (collection_id, document.filename)
        second_lock_key = (schema.collection_id, document.filename)

        first_lock_key, second_lock_key = sorted((
            first_lock_key, second_lock_key))

        first_file_lock = request.app.state.file_locks[first_lock_key]
        second_file_lock = request.app.state.file_locks[second_lock_key]

        async with first_file_lock, second_file_lock:

            # Does the filename exist in the target collection?
            filename_exists = await document_repository.select(
                collection_id__eq=schema.collection_id,
                filename__eq=document.filename)
            if filename_exists:
                raise E([LOC_BODY, "filename"], document.filename,
                        ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Is there a file in the current directory?
            current_file_path = os.path.join(
                config.DOCUMENTS_DIR, collection.name, document.filename)
            current_file_exists = await file_manager.isfile(current_file_path)
            if not current_file_exists:
                raise E([LOC_BODY, "filename"], document.filename,
                        ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

            # Is there a file in the target directory?
            target_file_path = os.path.join(
                config.DOCUMENTS_DIR, target_collection.name, document.filename)
            target_file_exists = await file_manager.isfile(target_file_path)
            if target_file_exists:
                raise E([LOC_BODY, "filename"], document.filename,
                        ERR_FILE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

            try:
                document.collection_id = target_collection.id
                await document_repository.update(document, commit=False)
                await file_manager.rename(current_file_path, target_file_path)
                await document_repository.commit()
                document_updated = True

            except Exception:
                await document_repository.rollback()
                log.exception(
                    "file move error; filename=%s; collection_id=%s;",
                    document.filename, target_collection.id,
                )
                raise E([LOC_BODY, "collection_id"], schema.collection_id,
                        ERR_FILE_WRITE_ERROR,
                        status.HTTP_422_UNPROCESSABLE_ENTITY)

    if not document_updated:
        await document_repository.update(document)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_UPDATE, document)

    request.state.log.debug("document updated; document_id=%s;", document_id)
    return {
        "document_id": document.id,
        "latest_revision_number": document.latest_revision_number,
    }
