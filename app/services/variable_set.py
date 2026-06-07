# app/services/variable_set.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ValueConflictError
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.models.variable import Variable
from app.repositories.orm import ORMRepository
from app.schemas.variable_path import VariablePath
from app.schemas.variable_set import VariableSetRequest

log = logging.getLogger(__name__)


async def set_variable(
    session: AsyncSession,
    user: User,
    data: VariableSetRequest,
    path: VariablePath,
) -> None:
    """
    Create or update a variable identified by namespace and variable key
    from the path. The serialized value from the body is stored as-is.
    """
    log.info("event=%s", E.VARIABLE_SET_STARTED)

    repository = ORMRepository(session)
    variable = await repository.select(
        Variable,
        namespace=path.namespace,
        variable_key=path.variable_key,
    )

    if variable is None:
        variable = Variable(
            namespace=path.namespace,
            variable_key=path.variable_key,
            variable_value=data.variable_value,
            created_by=user.id,
        )

        try:
            await repository.insert(variable)
        except IntegrityError:
            log.warning("event=%s", E.VARIABLE_SET_INSERT_CONFLICT)
            await repository.rollback()
            raise ValueConflictError(
                field="variable_key",
                input_value=path.variable_key,
            )

    else:
        variable.variable_value = data.variable_value
        variable.updated_by = user.id

        try:
            await repository.update(variable)
        except IntegrityError:
            log.warning("event=%s", E.VARIABLE_SET_UPDATE_CONFLICT)
            await repository.rollback()
            raise ValueConflictError(
                field="variable_key",
                input_value=path.variable_key,
            )

    await write_audit(
        repository=repository,
        event=E.VARIABLE_SET_COMPLETED,
        resource_type=Variable.__tablename__,
        resource_id=variable.id,
    )
    await repository.commit()

    log.info("event=%s variable_id=%s", E.VARIABLE_SET_COMPLETED, variable.id)
    await hooks.emit(E.VARIABLE_SET_COMPLETED, session, variable)
