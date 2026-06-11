# app/services/folder_write_protect.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.folder import Folder
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.folder_write_protect import FolderWriteProtectRequest

log = logging.getLogger(__name__)


async def change_folder_write_protect(
    session: AsyncSession,
    user: User,
    folder_id: int,
    data: FolderWriteProtectRequest,
) -> Folder:
    """
    Change a folder's explicit write-protection flag.
    """
    log.info("event=%s folder_id=%s", E.FOLDER_WRITE_PROTECT_STARTED, folder_id)  # noqa: E501

    repository = ORMRepository(session)
    folder = await repository.select(Folder, obj_id=folder_id)

    if folder is None:
        log.warning("event=%s", E.FOLDER_WRITE_PROTECT_FOLDER_NOT_FOUND)
        raise ResourceNotFoundError

    folder.is_write_protected = data.is_write_protected
    folder.updated_by = user.id

    await repository.update(folder)

    await write_audit(
        repository=repository,
        event=E.FOLDER_WRITE_PROTECT_COMPLETED,
        resource_type=Folder.__tablename__,
        resource_id=folder.id,
    )
    await repository.commit()

    log.info("event=%s", E.FOLDER_WRITE_PROTECT_COMPLETED)
    await hooks.emit(E.FOLDER_WRITE_PROTECT_COMPLETED, session, folder)

    return folder
