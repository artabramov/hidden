from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.comment_model import Comment
from app.schemas.collection_schemas import (
    CollectionUpdateRequest, CollectionUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_VALUE_DUPLICATED,
    HOOK_BEFORE_COLLECTION_UPDATE, HOOK_AFTER_COLLECTION_UPDATE)

router = APIRouter()


@router.put("/collection/{collection_id}", summary="Update a collection",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionUpdateResponse, tags=["Collections"])
@locked
async def collection_update(
    collection_id: int, schema: CollectionUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> CollectionUpdateResponse:
    """
    FastAPI router for updating a collection entity. The router
    retrieves the collection from the repository using the provided ID,
    ensures that the collection exists, and checks that the new
    collection name is unique. It updates the collection's attributes,
    executes related hooks, and returns the updated collection ID in
    a JSON response. The current user should have an editor role or
    higher. Returns a 200 response on success, a 404 error if the
    collection is not found, a 422 error if the collection name is
    duplicated, and a 403 error if authentication fails or the user
    does not have the required role.
    """
    collection_repository = Repository(session, cache, Collection)

    collection = await collection_repository.select(id=collection_id)
    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    collection_exists = await collection_repository.exists(
        collection_name__eq=schema.collection_name, id__ne=collection.id)
    if collection_exists:
        raise E([LOC_BODY, "collection_name"], schema.collection_name,
                ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    collection.is_locked = schema.is_locked
    collection.collection_name = schema.collection_name
    collection.collection_summary = schema.collection_summary
    await collection_repository.update(collection, commit=False)

    # Delete all related documents and comments from cache to avoid
    # possible side effects when collection transite its state between
    # locked and unlocked.

    document_repository = Repository(session, cache, Document)
    await document_repository.delete_all_from_cache()

    comment_repository = Repository(session, cache, Comment)
    await comment_repository.delete_all_from_cache()

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COLLECTION_UPDATE, collection)

    await collection_repository.commit()
    await hook.do(HOOK_AFTER_COLLECTION_UPDATE, collection)

    return {"collection_id": collection.id}
