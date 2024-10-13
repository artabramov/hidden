import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.document_schemas import DocumentReplaceResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import thumbnail_create
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DOCUMENT_REPLACE, HOOK_AFTER_DOCUMENT_REPLACE)

cfg = get_config()
router = APIRouter()


@router.post("/document/{document_id}", summary="Replace a document",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentReplaceResponse, tags=["Documents"])
@locked
async def document_replace(
    document_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentReplaceResponse:

    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    # upload file
    revision_filename = str(uuid.uuid4()) + cfg.REVISIONS_EXTENSION
    revision_path = os.path.join(cfg.REVISIONS_BASE_PATH, revision_filename)
    await FileManager.upload(file, revision_path)

    # create thumbnail
    thumbnail_filename = None
    try:
        mimetype = file.content_type
        thumbnail_filename = await thumbnail_create(revision_path, mimetype)
    except Exception:
        pass

    try:
        # encrypt file
        data = await FileManager.read(revision_path)
        encrypted_data = await FileManager.encrypt(data)
        await FileManager.write(revision_path, encrypted_data)

        # insert revision
        revision_repository = Repository(session, cache, Revision)
        revision = Revision(
            current_user.id, document.id, revision_filename,
            os.path.getsize(revision_path), file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # update latest_revision_id
        document.latest_revision_id = revision.id
        await document_repository.update(document, commit=False)

        # # update previous revision
        # revision_repository = Repository(session, cache, Revision)
        # document.latest_revision.is_latest = False
        # await revision_repository.update(
        #     document.latest_revision, commit=False)

        # update document counters and name
        await revision_repository.lock_all()
        document.revisions_count = await revision_repository.count_all(
            document_id__eq=document.id)
        document.revisions_size = await revision_repository.sum_all(
            "revision_size", document_id__eq=document.id)
        document.document_name = file.filename
        await document_repository.update(document, commit=False)

        # update collection counters
        if document.collection_id:
            await document_repository.lock_all()

            document.document_collection.revisions_count = (
                await document_repository.sum_all(
                    "revisions_count",
                    collection_id__eq=document.collection_id))

            document.document_collection.revisions_size = (
                await document_repository.sum_all(
                    "revisions_size",
                    collection_id__eq=document.collection_id))

            collection_repository = Repository(session, cache, Collection)
            await collection_repository.update(
                document.document_collection, commit=False)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(HOOK_BEFORE_DOCUMENT_REPLACE, document)

        await document_repository.commit()
        await hook.do(HOOK_AFTER_DOCUMENT_REPLACE, document)

    except Exception as e:
        await FileManager.delete(revision_path)
        if thumbnail_filename:
            thumbnail_path = os.path.join(
                cfg.THUMBNAILS_BASE_PATH, thumbnail_filename)
            await FileManager.delete(thumbnail_path)
        raise e

    return {
        "document_id": document.id,
        "revision_id": revision.id,
    }
