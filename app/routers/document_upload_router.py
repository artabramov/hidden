import os
import uuid
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.models.shard_model import Shard
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.document_schemas import DocumentUploadResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import is_image, thumbnail_create
from app.constants import (
    LOC_BODY, ERR_VALUE_INVALID, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DOCUMENT_UPLOAD, HOOK_AFTER_DOCUMENT_UPLOAD)
from app.errors import E
from app.helpers.encryption_helper import encrypt_bytes
from app.helpers.shuffle_helper import shuffle

cfg = get_config()
router = APIRouter()


@router.post("/collection/{collection_id}/document",
             summary="Upload a document.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentUploadResponse, tags=["Files"])
@locked
async def document_upload(
    collection_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> DocumentUploadResponse:
    """
    Upload a document. The router validates the provided collection,
    ensures it is not locked, processes the file (validating, encrypting,
    and creating a thumbnail if needed), splits it into shards, and
    creates a revision for the document. It then saves the document and
    revision details to the repository. The current user should have a
    writer role or higher. Returns a 201 response on success, a 422
    error if the collection is invalid, a 423 error if the collection
    or the application is locked, a 500 error if an unexpected failure
    occurs during file processing or shard creation, and a 403 error
    if authentication failed or the user does not have the required
    permissions.

    **Args:**
    - `collection_id`: The ID of the collection to upload the document
      to.
    - `file`: The file to be uploaded.

    **Returns:**
    - `DocumentUploadResponse`: The response schema containing the ID of
      the document and the latest revision.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required
      permissions.
    - `422 Unprocessable Entity`: Raised if the collection does not exist
      or is invalid.
    - `423 Locked`: Raised if the collection or the application is
      locked.
    - `500 Internal Server Error`: Raised if an error occurs during file
      processing, encryption, or shard creation.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `writer`, `editor` or `admin` roles are required to access this
      router.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_BODY, "collection_id"], collection_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif collection.is_locked:
        raise E([LOC_BODY, "collection_id"], collection_id,
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

        # insert document
        document_repository = Repository(session, cache, Document)
        document = Document(current_user.id, collection.id, file.filename)
        await document_repository.insert(document, commit=False)

        # insert revision
        revision_repository = Repository(session, cache, Revision)
        revision = Revision(
            current_user.id, document.id, file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # split encrypted file to shards
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
        document.document_size = revision.revision_size
        document.document_mimetype = revision.revision_mimetype
        document.thumbnail_filename = revision.thumbnail_filename
        document.latest_revision_id = revision.id
        await document_repository.update(document, commit=False)

        # shuffle
        if cfg.SHUFFLE_ENABLED:
            await shuffle(session, cache)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(HOOK_BEFORE_DOCUMENT_UPLOAD, document)

        await document_repository.commit()
        await hook.do(HOOK_AFTER_DOCUMENT_UPLOAD, document)

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
