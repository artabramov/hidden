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
from app.models.tag_model import Tag
from app.schemas.document_schemas import (
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.helpers.tag_helper import extract_tag_values
from app.errors import E
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    ERR_VALUE_INVALID, HOOK_BEFORE_DOCUMENT_UPDATE, HOOK_AFTER_DOCUMENT_UPDATE)

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}",
            summary="Update a document.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentUpdateResponse, tags=["Documents"])
@locked
async def document_update(
    document_id: int, schema: DocumentUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentUpdateResponse:
    """
    Update a document. The router fetches the document using the
    provided ID, checks if the associated collection is not locked, and
    if a partner ID is provided, validates the partner. It updates the
    document data and tags. Executes related hooks before and after
    committing the changes. Returns a 200 response on success, a 404
    error if the document is not found, a 423 error if the collection
    or the application is locked, a 422 error if arguments validation
    failed, and a 403 error if authentication failed or the user does
    not have the required permissions.

    **Args:**
    - `document_id`: The ID of the document to be updated.
    - `DocumentUpdateRequest`: The request schema containing the updated
    document information.

    **Returns:**
    - `DocumentUpdateResponse`: The response schema containing the ID of
    the updated document.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required
    permissions.
    - `404 Not Found`: Raised if the document with the provided ID does
    - `422 Unprocessable Entity`:  Raised if arguments validation failed.
    not exist.
    - `423 Locked`: Raised if the collection or the application is
    locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `editor` or `admin` roles are required to access this router.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(
        id=schema.collection_id)

    if not collection:
        raise E([LOC_BODY, "collection_id"], schema.collection_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif collection.is_locked:
        raise E([LOC_BODY, "collection_id"], schema.collection_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    revision_repository = Repository(session, cache, Revision)
    document.latest_revision = await revision_repository.select(
        id=document.latest_revision_id)

    # If a partner ID is received, then validate the partner.

    if schema.partner_id:
        partner_repository = Repository(session, cache, Partner)
        partner = await partner_repository.select(id=schema.partner_id)

        if not partner:
            raise E([LOC_BODY, "partner_id"], schema.partner_id,
                    ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Update the data of the document itself.

    document.collection_id = schema.collection_id
    document.partner_id = schema.partner_id
    document.is_flagged = schema.is_flagged
    document.document_filename = schema.document_filename
    document.document_summary = schema.document_summary
    await document_repository.update(document, commit=False)

    # Update the original filename for the latest revision
    # associated with the document.

    if document.latest_revision.revision_filename != document.document_filename:  # noqa E501
        document.latest_revision.revision_filename = document.document_filename

        await revision_repository.update(
            document.latest_revision, commit=False)

    # Update tags associated with the document.

    tag_repository = Repository(session, cache, Tag)
    await tag_repository.delete_all(document_id__eq=document_id,
                                    commit=False)

    tag_values = extract_tag_values(schema.document_tags)
    tag_repository = Repository(session, cache, Tag)
    for value in tag_values:
        try:
            tag = Tag(document_id, value)
            await tag_repository.insert(tag, commit=False)
        except Exception:
            pass

    # Execute the corresponding hooks before and
    # after committing the changes

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DOCUMENT_UPDATE, document)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_DOCUMENT_UPDATE, document)

    return {
        "document_id": document.id,
        "revision_id": document.latest_revision_id,
    }
