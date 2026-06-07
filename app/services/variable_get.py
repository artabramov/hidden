# app/services/variable_get.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.variable import Variable
from app.repositories.orm import ORMRepository
from app.schemas.variable_path import VariablePath

log = logging.getLogger(__name__)


async def get_variable(
    session: AsyncSession,
    path: VariablePath,
) -> Variable:
    """
    Retrieve a variable identified by namespace and variable key.
    Raises ResourceNotFoundError when the variable does not exist.
    """
    log.info("event=%s", E.VARIABLE_GET_STARTED)

    repository = ORMRepository(session)
    variable = await repository.select(
        Variable,
        namespace=path.namespace,
        variable_key=path.variable_key,
    )

    if variable is None:
        log.warning("event=%s", E.VARIABLE_GET_VARIABLE_NOT_FOUND)
        raise ResourceNotFoundError

    log.info("event=%s variable_id=%s", E.VARIABLE_GET_COMPLETED, variable.id)
    await hooks.emit(E.VARIABLE_GET_COMPLETED, session, variable)
    return variable
