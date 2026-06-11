# app/services/variable_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.variable import Variable
from app.repositories.orm import ORMRepository
from app.schemas.variable_path import VariablePath

log = logging.getLogger(__name__)


async def delete_variable(
    session: AsyncSession,
    path: VariablePath,
) -> None:
    """
    Delete a variable identified by namespace and variable key from the
    path. Raises ResourceNotFoundError when the variable does not exist.
    """
    log.info("event=%s", E.VARIABLE_DELETE_STARTED)

    repository = ORMRepository(session)
    variable = await repository.select(
        Variable,
        namespace=path.namespace,
        variable_key=path.variable_key,
    )

    if variable is None:
        log.warning("event=%s", E.VARIABLE_DELETE_VARIABLE_NOT_FOUND)
        raise ResourceNotFoundError

    await repository.delete(variable)

    await write_audit(
        repository=repository,
        event=E.VARIABLE_DELETE_COMPLETED,
        resource_type=Variable.__tablename__,
        resource_id=variable.id,
    )
    await repository.commit()

    log.info("event=%s variable_id=%s", E.VARIABLE_DELETE_COMPLETED, variable.id)  # noqa: E501
    await hooks.emit(E.VARIABLE_DELETE_COMPLETED, session, variable)
