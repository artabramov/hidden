from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.collection_model import Collection
from app.repository import Repository
from app.schemas.collection_insert import (
    CollectionInsertRequest, CollectionInsertResponse)
from app.hook import Hook, HOOK_AFTER_COLLECTION_INSERT

router = APIRouter()


@router.post("/collection", summary="Create a new collection.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=CollectionInsertResponse, tags=["Collections"])
async def collection_insert(
    request: Request, schema: CollectionInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache)
) -> CollectionInsertResponse:
    """
    Creates a new collection. Checks if the collection name is unique,
    and creates a new collection with the provided name and summary.
    """
    collection = Collection(
        collection_name=schema.collection_name,
        collection_summary=schema.collection_summary,
        readonly=schema.readonly,
        private=schema.private,
    )

    collection_repository = Repository(
        session, cache, Collection, request.app.state.config
    )
    await collection_repository.insert(collection)

    request.state.log.debug(
        "collection created; collection_id=%s", collection.id
    )

    hook = Hook(request, session, cache, None)
    await hook.call(HOOK_AFTER_COLLECTION_INSERT, collection)

    return {"collection_id": collection.id}
