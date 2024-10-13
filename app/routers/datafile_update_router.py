from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.member_model import Member
from app.models.datafile_model import Datafile
from app.models.revision_model import Revision
from app.schemas.datafile_schemas import (
    DatafileUpdateRequest, DatafileUpdateResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.libraries.tag_library import TagLibrary
from app.errors import E
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    ERR_VALUE_INVALID, HOOK_BEFORE_DATAFILE_UPDATE, HOOK_AFTER_DATAFILE_UPDATE)

cfg = get_config()
router = APIRouter()


@router.put("/datafile/{datafile_id}",
            summary="Update a datafile data",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DatafileUpdateResponse, tags=["Datafiles"])
@locked
async def datafile_update(
    datafile_id: int, schema: DatafileUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DatafileUpdateResponse:

    # Validate the datafile.

    datafile_repository = Repository(session, cache, Datafile)
    datafile = await datafile_repository.select(id=datafile_id)

    if not datafile:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif datafile.is_locked:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    revision_repository = Repository(session, cache, Revision)
    datafile.latest_revision = await revision_repository.select(
        id=datafile.latest_revision_id)

    # If a member ID is received, then validate the memeber.

    if schema.member_id:
        member_repository = Repository(session, cache, Member)
        member = await member_repository.select(id=schema.member_id)

        if not member:
            raise E([LOC_BODY, "member_id"], schema.member_id,
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

    # Update the data of the datafile itself.

    datafile.collection_id = schema.collection_id
    datafile.member_id = schema.member_id
    datafile.datafile_name = schema.datafile_name
    datafile.datafile_summary = schema.datafile_summary
    await datafile_repository.update(datafile, commit=False)

    # If a collection ID is received, then update
    # the collection's counters.

    if collection:
        await datafile_repository.lock_all()

        collection.datafiles_count = await datafile_repository.count_all(
            collection_id__eq=collection.id)

        collection.revisions_count = await datafile_repository.sum_all(
            "revisions_count", collection_id__eq=collection.id)

        collection.revisions_size = await datafile_repository.sum_all(
            "revisions_size", collection_id__eq=collection.id)

        await collection_repository.update(collection, commit=False)

    # If the datafile already has a related collection,
    # then update the collection's counters.

    if datafile.datafile_collection:
        await datafile_repository.lock_all()

        datafile.datafile_collection.datafiles_count = (
            await datafile_repository.count_all(
                collection_id__eq=datafile.datafile_collection.id))

        datafile.datafile_collection.revisions_count = (
            await datafile_repository.sum_all(
                "revisions_count",
                collection_id__eq=datafile.datafile_collection.id))

        datafile.datafile_collection.revisions_size = (
            await datafile_repository.sum_all(
                "revisions_size",
                collection_id__eq=datafile.datafile_collection.id))

        await collection_repository.update(
            datafile.datafile_collection, commit=False)

    # Update the original filename for the latest revision
    # associated with the datafile.

    if datafile.latest_revision.original_filename != datafile.datafile_name:
        datafile.latest_revision.original_filename = datafile.datafile_name

        revision_repository = Repository(session, cache, Revision)
        await revision_repository.update(
            datafile.latest_revision, commit=False)

    # Update tags associated with the datafile.

    tag_library = TagLibrary(session, cache)
    await tag_library.delete_all(datafile.id, commit=False)

    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(datafile.id, tag_values, commit=False)

    # Execute the corresponding hooks before and
    # after committing the changes

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DATAFILE_UPDATE, datafile)

    await datafile_repository.commit()
    await hook.do(HOOK_AFTER_DATAFILE_UPDATE, datafile)

    return {
        "datafile_id": datafile.id,
        "revision_id": datafile.latest_revision.id,
    }
