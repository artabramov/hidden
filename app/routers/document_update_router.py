from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.partner_model import Partner
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.schemas.document_schemas import (
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.libraries.tag_library import TagLibrary
from app.errors import E
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    ERR_VALUE_INVALID, HOOK_BEFORE_DOCUMENT_UPDATE, HOOK_AFTER_DOCUMENT_UPDATE)

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}",
            summary="Update a document data",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentUpdateResponse, tags=["Documents"])
@locked
async def document_update(
    document_id: int, schema: DocumentUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentUpdateResponse:

    # Validate the document.

    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    revision_repository = Repository(session, cache, Revision)
    document.latest_revision = await revision_repository.select(
        id=document.latest_revision_id)

    # If a partner ID is received, then validate the memeber.

    if schema.partner_id:
        partner_repository = Repository(session, cache, Partner)
        partner = await partner_repository.select(id=schema.partner_id)

        if not partner:
            raise E([LOC_BODY, "partner_id"], schema.partner_id,
                    ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    # If a collection ID is received, then validate the collection.

    collection = None
    if schema.collection_id:
        collection_repository = Repository(session, cache, Collection)
        collection = await collection_repository.select(
            id=schema.collection_id)

        if not collection:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        elif collection.is_locked:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    # Update the data of the document itself.

    document.collection_id = schema.collection_id
    document.partner_id = schema.partner_id
    document.document_name = schema.document_name
    document.document_summary = schema.document_summary
    await document_repository.update(document, commit=False)

    # If a collection ID is received, then update
    # the collection's counters.

    if collection:
        await document_repository.lock_all()

        collection.documents_count = await document_repository.count_all(
            collection_id__eq=collection.id)

        await collection_repository.update(collection, commit=False)

    # If the document already has a related collection,
    # then update the collection's counters.

    if document.document_collection:
        await document_repository.lock_all()

        document.document_collection.documents_count = (
            await document_repository.count_all(
                collection_id__eq=document.document_collection.id))

        await collection_repository.update(
            document.document_collection, commit=False)

    # Update the original filename for the latest revision
    # associated with the document.

    if document.latest_revision.original_filename != document.document_name:
        document.latest_revision.original_filename = document.document_name

        revision_repository = Repository(session, cache, Revision)
        await revision_repository.update(
            document.latest_revision, commit=False)

    # Update tags associated with the document.

    tag_library = TagLibrary(session, cache)
    await tag_library.delete_all(document.id, commit=False)

    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(document.id, tag_values, commit=False)

    # Execute the corresponding hooks before and
    # after committing the changes

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DOCUMENT_UPDATE, document)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_DOCUMENT_UPDATE, document)

    return {
        "document_id": document.id,
        "revision_id": document.latest_revision.id,
    }
