import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.models.shard_model import Shard
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.document_schemas import DocumentReplaceResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import is_image, thumbnail_create
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DOCUMENT_REPLACE, HOOK_AFTER_DOCUMENT_REPLACE)
from app.helpers.encryption_helper import encrypt_bytes
from app.helpers.shuffle_helper import shuffle

cfg = get_config()
router = APIRouter()


@router.post("/document/{document_id}",
             summary="Replace the latest revision of a document.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentReplaceResponse, tags=["Files"])
@locked
async def document_replace(
    document_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentReplaceResponse:
    """
    Replace the latest revision of a document. The router allows to
    upload a new version of the document, replace its latest revision,
    and update the document's metadata. The file is encrypted, split
    into shards, and stored securely. The current user must have the
    editor role or higher. Returns a 201 response on success, a 404
    error if the document is not found, a 401 error if authentication
    failed or the user does not have the required permissions, a 403
    error if the token is missing, a 423 error if the collection
    or the application is locked, and a 422 error if the file
    is invalid.

    **Args:**
    - `document_id`: The ID of the document to be replaced.
    - `file`: The new file to replace the current document revision.

    **Returns:**
    - `DocumentReplaceResponse`: The response schema containing the
    document's ID and the revision ID of the newly added revision.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `404 Not Found`: Raised if the document with the specified ID does
    not exist.
    - `422 Unprocessable Entity`: Raised if the uploaded file is invalid
    or cannot be processed.
    - `423 Locked`: Raised if the collection or the document is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `editor` or `admin` user role is required to access this router.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    thumbnail_filename = None
    shard_filenames = []

    # create temporary file
    temp_path = os.path.join(cfg.TEMP_PATH, str(uuid.uuid4()))
    await FileManager.upload(file, temp_path)

    # create thumbnail
    if is_image(file.content_type):
        thumbnail_filename = await thumbnail_create(temp_path)

    try:
        # encrypt file
        data = await FileManager.read(temp_path)
        encrypted_data = encrypt_bytes(data)
        await FileManager.write(temp_path, encrypted_data)

        # insert revision
        revision_repository = Repository(session, cache, Revision)
        revision = Revision(
            current_user.id, document.id, file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # split file to shards
        shard_filenames = await FileManager.split(
            encrypted_data, cfg.SHARD_BASE_PATH, cfg.SHARD_SIZE)
        shard_repository = Repository(session, cache, Shard)
        for shard_index, shard_filename in enumerate(shard_filenames):
            shard = Shard(
                current_user.id, revision.id, shard_filename, shard_index)
            await shard_repository.insert(shard, commit=False)

        # delete temporary file
        await FileManager.delete(temp_path)

        # update latest_revision_id
        document.latest_revision_id = revision.id
        await document_repository.update(document, commit=False)

        # update document data
        document.document_filename = revision.revision_filename
        document.document_size = revision.revision_size
        document.document_mimetype = revision.revision_mimetype
        document.thumbnail_filename = revision.thumbnail_filename
        await document_repository.update(document, commit=False)

        # shuffle
        if cfg.SHUFFLE_ENABLED:
            await shuffle(session, cache)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(HOOK_BEFORE_DOCUMENT_REPLACE, document)

        await document_repository.commit()
        await hook.do(HOOK_AFTER_DOCUMENT_REPLACE, document)

    except Exception as e:
        await FileManager.delete(temp_path)

        if thumbnail_filename:
            await FileManager.delete(os.path.join(
                cfg.THUMBNAILS_BASE_PATH, thumbnail_filename))

        if shard_filenames:
            for shard_filename in shard_filenames:
                await FileManager.delete(os.path.join(
                    cfg.SHARD_BASE_PATH, shard_filename))

        raise e

    return {
        "document_id": document.id,
        "revision_id": revision.id,
    }
