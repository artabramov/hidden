"""FastAPI router for document changing."""

from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.document_update import (
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.validators.file_validators import name_validate
from app.hook import Hook, HOOK_AFTER_DOCUMENT_UPDATE
from app.auth import auth
from app.repository import Repository
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_VALUE_INVALID,
    ERR_FILE_CONFLICT)

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
    locks are acquired in a deterministic order to prevent deadlocks.
    All database and filesystem checks are executed inside this critical
    section. These locks are in-process.

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
    - `collection_id` (integer ≥ 1) — current collection identifier.
    - `document_id` (integer ≥ 1) — document identifier.

    **Request body:**
    - `application/json` with any of: `filename`, `summary`,
    `collection_id`.

    **Response codes:**
    - `200` — update successful.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or document not found.
    - `409` — conflict: name already exists in DB/FS or DB/FS mismatch
    (document present but file missing, or vice versa).
    - `422` — invalid file name.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_UPDATE` — executed after a successful update.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    collection_locks = request.app.state.collection_locks
    file_locks = request.app.state.file_locks

    # NOTE: On document update, keep two-step fetch to hit Redis cache;
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

    document.summary = schema.summary
    document_updated = False

    # Checking the correctness of the file name
    try:
        filename = name_validate(schema.filename)
    except ValueError:
        raise E([LOC_BODY, "file"], schema.filename, ERR_VALUE_INVALID,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    # NOTE: On document update, a small TOCTOU window remains; for
    # strict guarantees, revalidate entities under the locks right
    # before rename/move.

    # Rename the file if the filename changes
    if document.filename != filename:

        # NOTE: On file rename, acquire the collection READ lock first,
        # then the per-file exclusive lock.

        collection_lock = collection_locks[collection_id]

        first_lock_key = (collection_id, document.filename)
        second_lock_key = (collection_id, filename)

        first_lock_key, second_lock_key = sorted((
            first_lock_key, second_lock_key))

        first_file_lock = file_locks[first_lock_key]
        second_file_lock = file_locks[second_lock_key]

        async with collection_lock.read(), first_file_lock, second_file_lock:

            # Check the document with the filename in the collection
            filename_exists = await document_repository.select(
                id__ne=document.id, filename__eq=filename,
                collection_id__eq=collection.id)
            if filename_exists:
                raise E([LOC_BODY, "file"], filename,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            # Check the file with the current filename in the directory
            current_file_path = document.path(config)
            current_file_exists = await file_manager.isfile(current_file_path)
            if not current_file_exists:
                raise E([LOC_BODY, "file"], document.filename,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            # Check the file with the new filename in the directory
            updated_file_path = Document.path_for_filename(
                config, collection.name, filename)
            updated_file_exists = await file_manager.isfile(updated_file_path)
            if updated_file_exists:
                raise E([LOC_BODY, "file"], filename,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            try:
                document.filename = filename
                await document_repository.update(document, commit=False)
                await file_manager.rename(current_file_path, updated_file_path)
                lru.delete(current_file_path)
                lru.delete(updated_file_path)

                await document_repository.commit()
                document_updated = True

            except Exception:
                await document_repository.rollback()
                raise

    # Move the file if collection changes
    if document.collection_id != schema.collection_id:

        # Does the target collection exist?
        target_collection = await collection_repository.select(
            id=schema.collection_id)
        if not target_collection:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        # NOTE: On file move, acquire READ locks on both collections
        # first, then the per-file exclusive lock on both file paths;

        cid_a, cid_b = sorted([document.collection_id, schema.collection_id])
        collection_lock_a = collection_locks[cid_a]
        collection_lock_b = collection_locks[cid_b]

        async with collection_lock_a.read(), collection_lock_b.read():
            first_lock_key = (collection_id, document.filename)
            second_lock_key = (schema.collection_id, document.filename)

            first_lock_key, second_lock_key = sorted((
                first_lock_key, second_lock_key))

            first_file_lock = file_locks[first_lock_key]
            second_file_lock = file_locks[second_lock_key]

            async with first_file_lock, second_file_lock:

                # Does the filename exist in the target collection?
                filename_exists = await document_repository.select(
                    collection_id__eq=schema.collection_id,
                    filename__eq=document.filename)
                if filename_exists:
                    raise E([LOC_BODY, "file"], document.filename,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                # Is there a file in the current directory?
                current_file_path = document.path(config)
                current_file_exists = await file_manager.isfile(
                    current_file_path)
                if not current_file_exists:
                    raise E([LOC_BODY, "file"], document.filename,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                # Is there a file in the target directory?
                target_file_path = Document.path_for_filename(
                    config, target_collection.name, document.filename)
                target_file_exists = await file_manager.isfile(
                    target_file_path)

                if target_file_exists:
                    raise E([LOC_BODY, "file"], document.filename,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                try:
                    document.collection_id = target_collection.id
                    await document_repository.update(document, commit=False)
                    await file_manager.rename(
                        current_file_path, target_file_path)
                    lru.delete(current_file_path)
                    lru.delete(target_file_path)

                    await document_repository.commit()
                    document_updated = True

                except Exception:
                    await document_repository.rollback()
                    raise

    if not document_updated:
        await document_repository.update(document)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_UPDATE, document)

    return {
        "document_id": document.id,
        "latest_revision_number": document.latest_revision_number,
    }
