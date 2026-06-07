# app/services/file_tag_add.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.file import File
from app.models.file_tag import FileTag
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.file_tag_add import FileTagAddRequest

log = logging.getLogger(__name__)


async def add_file_tag(
    session: AsyncSession,
    user: User,
    file_id: int,
    data: FileTagAddRequest,
) -> None:
    """
    Add a tag to an existing file. The operation is idempotent: if the
    file already has the tag, no new row is created.
    """
    log.info("event=%s file_id=%s", E.TAG_ADD_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.TAG_ADD_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(file.file_folder)

    if (
        file.file_folder.is_write_protected or
        file.file_folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.TAG_ADD_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    existing_tag = await repository.select(
        FileTag,
        file_id=file.id,
        tag=data.tag,
    )

    if existing_tag is not None:
        return

    tag = FileTag(
        file_id=file.id,
        created_by=user.id,
        tag=data.tag,
    )

    try:
        await repository.insert(tag)

    except IntegrityError:
        await repository.rollback()
        return

    await write_audit(
        repository=repository,
        event=E.TAG_ADD_COMPLETED,
        resource_type=FileTag.__tablename__,
        resource_id=tag.id,
    )
    await repository.commit()

    log.info("event=%s tag_id=%s", E.TAG_ADD_COMPLETED, tag.id)
    await hooks.emit(E.TAG_ADD_COMPLETED, session, tag)
