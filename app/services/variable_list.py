# app/services/variable_list.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.events import Events as E
from app.hooks import hooks
from app.models.variable import Variable
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)


async def list_variables(
    session: AsyncSession,
    namespace: str,
) -> list[Variable]:
    """
    Retrieve all variables for the given namespace.
    """
    log.info("event=%s", E.VARIABLE_LIST_STARTED)

    repository = ORMRepository(session)
    variables = await repository.select_all(
        Variable,
        namespace=namespace,
    )

    log.info("event=%s", E.VARIABLE_LIST_COMPLETED)
    await hooks.emit(E.VARIABLE_LIST_COMPLETED, session, variables)
    return variables
