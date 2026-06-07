# app/services/folder_list.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.folder import Folder
from app.repositories.orm import ORMRepository
from app.schemas.folder_list import FolderListRequest

log = logging.getLogger(__name__)


async def list_folders(
    session: AsyncSession,
    params: FolderListRequest,
) -> tuple[list[Folder], int, bool]:
    """
    Return direct child folders for the parent indicated by
    params.parent_id__eq (None for the hierarchy root) together
    with the total number of matching folders and parent recursive
    write-protection state.
    """
    parent_id = params.parent_id__eq
    log.info("event=%s parent_id=%s", E.FOLDER_LIST_STARTED, parent_id)

    repository = ORMRepository(session)
    is_write_protected_recursive = False

    filters = params.model_dump(
        exclude_none=True,
        exclude={"parent_id__eq"},
    )

    if parent_id is None:
        filters["parent_id__is"] = None

    else:
        parent = await repository.select(Folder, obj_id=parent_id)

        if parent is None:
            log.warning("event=%s", E.FOLDER_LIST_PARENT_NOT_FOUND)
            raise ResourceNotFoundError

        parent_chain = await repository.select_parent_chain(parent)
        is_write_protected_recursive = (
            parent.is_write_protected
            or parent.is_write_protected_recursive(parent_chain)
        )
        filters["parent_id__eq"] = parent_id

    folders_count = await repository.count_all(Folder, **filters)
    folders = await repository.select_all(Folder, **filters)

    log.info("event=%s", E.FOLDER_LIST_COMPLETED)
    await hooks.emit(E.FOLDER_LIST_COMPLETED, session, folders)
    return folders, folders_count, is_write_protected_recursive
