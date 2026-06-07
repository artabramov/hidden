# app/services/file_starred_change.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.file import File
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.file_starred_change import FileStarredChangeRequest

log = logging.getLogger(__name__)


async def change_file_starred(
    session: AsyncSession,
    user: User,
    file_id: int,
    data: FileStarredChangeRequest,
) -> File:
    """
    Change the starred flag for an existing file.
    """
    log.info("event=%s file_id=%s", E.FILE_STARRED_CHANGE_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_STARRED_CHANGE_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    file.is_starred = data.is_starred
    file.updated_by = user.id

    await repository.update(file)

    await write_audit(
        repository=repository,
        event=E.FILE_STARRED_CHANGE_COMPLETED,
        resource_type=File.__tablename__,
        resource_id=file.id,
    )
    await repository.commit()

    log.info("event=%s", E.FILE_STARRED_CHANGE_COMPLETED)
    await hooks.emit(E.FILE_STARRED_CHANGE_COMPLETED, session, file)

    return file
