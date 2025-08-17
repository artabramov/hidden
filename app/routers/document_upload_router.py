import os
import uuid
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.collection_model import Collection
from app.models.shard_model import Shard
from app.hook import Hook, HOOK_AFTER_DOCUMENT_UPLOAD
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.document_upload_schema import DocumentUploadResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import image_resize, IMAGE_MIMETYPES
from app.helpers.video_helper import video_capture, VIDEO_MIMETYPES
from app.helpers.encrypt_helper import encrypt_bytes
from app.helpers.shuffle_helper import shuffle_shards
from app.error import E, LOC_BODY, ERR_VALUE_NOT_FOUND
from app.libraries.collection_library import CollectionLibrary

cfg = get_config()
router = APIRouter()


@router.post("/document", summary="Upload a document.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentUploadResponse, tags=["Documents"])
async def document_upload(
    file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> DocumentUploadResponse:
    """
    Uploads a document. Processes the uploaded file by generating a
    secure unique filename, encrypting its contents, and optionally
    generating and encrypting a thumbnail if the file is an image or
    video. Creates a new document and associates it with the specified
    collection, if provided. If the document is linked to a collection,
    the collection's thumbnail is also regenerated after upload.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `writer`, `editor`, or `admin` role.

    **Returns:**
    - `DocumentUploadResponse`: Response on success.

    **Responses:**
    - `201 Created`: If the document is successfully uploaded and saved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the secret key is missing.
    - `404 Not Found`: If the specified collection does not exist.
    - `422 Unprocessable Entity`: If validation of the file fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_UPLOAD`: Executes after the document is
    successfully created.
    """
    return await _document_upload(file, session, cache, current_user)


@router.post("/collection/{collection_id}/document",
             summary="Upload a document to the collection.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentUploadResponse, tags=["Collections"])
async def document_upload_to_collection(
    file: UploadFile = File(...), collection_id: int = None,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> DocumentUploadResponse:
    return await _document_upload(
        file, session, cache, current_user, collection_id)


async def _document_upload(file: UploadFile, session, cache,
                           current_user: User, collection_id: int = None):
    collection = None
    if collection_id:
        collection_repository = Repository(session, cache, Collection)
        collection = await collection_repository.select(id=collection_id)

        if not collection:
            raise E([LOC_BODY, "collection_id"], collection_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    document_filename = str(uuid.uuid4())
    document_path = os.path.join(cfg.DOCUMENTS_PATH, document_filename)
    thumbnail_filename, thumbnail_path = None, None

    original_filename = file.filename
    document_mimetype = await FileManager.mimetype(file.filename)
    document_filesize = file.size

    try:
        await FileManager.upload(file, document_path)

        if document_mimetype in IMAGE_MIMETYPES + VIDEO_MIMETYPES:
            thumbnail_filename = str(uuid.uuid4())
            thumbnail_path = os.path.join(
                cfg.THUMBNAILS_PATH, thumbnail_filename)

        if document_mimetype in IMAGE_MIMETYPES:
            await FileManager.copy(document_path, thumbnail_path)

        elif document_mimetype in VIDEO_MIMETYPES:
            await video_capture(document_path, thumbnail_path)

        if document_mimetype in IMAGE_MIMETYPES + VIDEO_MIMETYPES:
            await image_resize(
                thumbnail_path, cfg.THUMBNAILS_WIDTH,
                cfg.THUMBNAILS_HEIGHT, cfg.THUMBNAILS_QUALITY)

            thumbnail_data = await FileManager.read(thumbnail_path)
            encrypted_thumbnail_data = encrypt_bytes(thumbnail_data)
            await FileManager.write(thumbnail_path, encrypted_thumbnail_data)

        document_data = await FileManager.read(document_path)
        encrypted_document_data = encrypt_bytes(document_data)

        document_repository = Repository(session, cache, Document)
        document = Document(
            current_user.id, original_filename, document_filename,
            document_filesize, document_mimetype,
            collection_id=collection_id,
            thumbnail_filename=thumbnail_filename)
        await document_repository.insert(document)

        # split encrypted file to shards
        shard_filenames = await FileManager.split(
            encrypted_document_data, cfg.DOCUMENTS_PATH)
        shard_repository = Repository(session, cache, Shard)
        for shard_index, shard_filename in enumerate(shard_filenames):
            shard = Shard(document.id, shard_filename, shard_index)
            await shard_repository.insert(shard, commit=False)

        # delete source file
        await FileManager.delete(document_path)

        if collection:
            collection_library = CollectionLibrary(session, cache)
            await collection_library.create_thumbnail(collection_id)

        await shuffle_shards(session, cache)

        hook = Hook(session, cache, current_user=current_user)
        await hook.call(HOOK_AFTER_DOCUMENT_UPLOAD, document)

    except Exception as e:
        await FileManager.delete(document_path)
        if thumbnail_path:
            await FileManager.delete(thumbnail_path)

        raise e

    return {
        "document_id": document.id,
    }
