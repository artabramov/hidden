# app/services/folder_select.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.folder import Folder
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)


async def select_folder(
    session: AsyncSession,
    folder_id: int,
) -> tuple[Folder, bool]:
    """
    Retrieve a folder by identifier and return the selected folder
    record together with its recursive write-protection state.
    """
    log.info("event=%s folder_id=%s", E.FOLDER_SELECT_STARTED, folder_id)

    repository = ORMRepository(session)
    folder = await repository.select(Folder, obj_id=folder_id)

    if folder is None:
        log.warning("event=%s", E.FOLDER_SELECT_FOLDER_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(folder)
    is_write_protected_recursive = folder.is_write_protected_recursive(
        parent_chain,
    )

    log.info("event=%s", E.FOLDER_SELECT_COMPLETED)
    await hooks.emit(E.FOLDER_SELECT_COMPLETED, session, folder)
    return folder, is_write_protected_recursive
