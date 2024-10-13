from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.schemas.document_schemas import DocumentDeleteResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DOCUMENT_DELETE, HOOK_AFTER_DOCUMENT_DELETE)

router = APIRouter()


@router.delete("/document/{document_id}", summary="Delete a document",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=DocumentDeleteResponse, tags=["Documents"])
@locked
async def document_delete(
    document_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DocumentDeleteResponse:
    """
    FastAPI router for deleting a document entity. The router retrieves
    the document from the repository using the provided ID, checks if
    the document exists and its collection is not locked, deletes the
    document and all related entities, updates the counters for the
    associated collection, executes related hooks, and returns the
    deleted document ID in a JSON response. The current user should
    have an admin role. Returns a 200 response on success, a 404 error
    if the document is not found, a 423 error if the collection is
    locked, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    await document_repository.delete(document, commit=False)

    if document.collection_id:
        await document_repository.lock_all()

        document.document_collection.documents_count = (
            await document_repository.count_all(
                collection_id__eq=document.collection_id))

        document.document_collection.revisions_count = (
            await document_repository.sum_all(
                "revisions_count", collection_id__eq=document.collection_id))

        document.document_collection.revisions_size = (
            await document_repository.sum_all(
                "revisions_size", collection_id__eq=document.collection_id))

        collection_repository = Repository(session, cache, Collection)
        await collection_repository.update(
            document.document_collection, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DOCUMENT_DELETE, document)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_DOCUMENT_DELETE, document)

    return {"document_id": document.id}
