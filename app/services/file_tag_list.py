# app/services/file_tag_list.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.events import Events as E
from app.hooks import hooks
from app.models.file_tag import FileTag
from app.schemas.file_tag_list import TagListRequest

log = logging.getLogger(__name__)


async def list_tags(
    session: AsyncSession,
    params: TagListRequest,
) -> list[tuple[str, int]]:
    """
    Return the most frequently used tags ordered by usage count
    descending and capped at params.limit entries.
    """
    log.info("event=%s", E.TAG_LIST_STARTED)

    query = (
        select(FileTag.tag, func.count().label("usage_count"))
        .group_by(FileTag.tag)
        .order_by(func.count().desc())
        .limit(params.limit)
    )

    result = await session.execute(query)
    tags = [(row.tag, row.usage_count) for row in result.all()]

    log.info("event=%s", E.TAG_LIST_COMPLETED)
    await hooks.emit(E.TAG_LIST_COMPLETED, session, tags)
    return tags
