# tests/services/test_variable_set.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.exc import IntegrityError

from app.errors import ValueConflictError
from app.events import Events as E
from app.models.variable import Variable
from app.services.variable_set import set_variable


class TestSetVariable(unittest.IsolatedAsyncioTestCase):
    async def test_creates_new_variable_and_emits_hook(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.variable_value = {"k": "v"}

        path = MagicMock()
        path.namespace = "system"
        path.variable_key = "theme"

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.variable_set.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_set.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.variable_set.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await set_variable(session, user, data, path)

        repository.select.assert_awaited_once_with(
            Variable,
            namespace="system",
            variable_key="theme",
        )
        repository.insert.assert_awaited_once()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        args, kwargs = repository.insert.await_args
        variable = args[0]

        self.assertIsInstance(variable, Variable)
        self.assertEqual(variable.namespace, "system")
        self.assertEqual(variable.variable_key, "theme")
        self.assertEqual(variable.variable_value, {"k": "v"})
        self.assertEqual(variable.created_by, 123)
        self.assertIsNone(variable.updated_by)
        self.assertEqual(kwargs, {})
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.VARIABLE_SET_COMPLETED,
            session,
            variable,
        )

    async def test_updates_existing_variable_and_emits_hook(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 456

        data = MagicMock()
        data.variable_value = ["new", "value"]

        path = MagicMock()
        path.namespace = "system"
        path.variable_key = "theme"

        variable = Variable(
            namespace="system",
            variable_key="theme",
            variable_value="old",
            created_by=100,
        )
        variable.updated_by = None

        repository = AsyncMock()
        repository.select.return_value = variable

        with (
            patch(
                "app.services.variable_set.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_set.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.variable_set.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await set_variable(session, user, data, path)

        repository.select.assert_awaited_once_with(
            Variable,
            namespace="system",
            variable_key="theme",
        )
        repository.insert.assert_not_awaited()
        repository.update.assert_awaited_once_with(variable)
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()

        self.assertEqual(variable.variable_value, ["new", "value"])
        self.assertEqual(variable.updated_by, 456)

        emit_mock.assert_awaited_once_with(
            E.VARIABLE_SET_COMPLETED,
            session,
            variable,
        )

    async def test_raises_value_conflict_on_insert_integrity_error(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 123

        data = MagicMock()
        data.variable_value = {"k": "v"}

        path = MagicMock()
        path.namespace = "system"
        path.variable_key = "theme"

        repository = AsyncMock()
        repository.select.return_value = None
        repository.insert.side_effect = IntegrityError(None, None, None)

        with (
            patch(
                "app.services.variable_set.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_set.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueConflictError) as cm:
                await set_variable(session, user, data, path)

        repository.insert.assert_awaited_once()
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

        error = cm.exception

        self.assertEqual(error.loc, ("body", "variable_key"))
        self.assertEqual(error.error_type, "value_conflict")
        self.assertEqual(error.input_value, "theme")

    async def test_raises_value_conflict_on_update_integrity_error(self):
        session = AsyncMock()

        user = MagicMock()
        user.id = 456

        data = MagicMock()
        data.variable_value = "new-value"

        path = MagicMock()
        path.namespace = "system"
        path.variable_key = "theme"

        variable = Variable(
            namespace="system",
            variable_key="theme",
            variable_value="old-value",
            created_by=100,
        )

        repository = AsyncMock()
        repository.select.return_value = variable
        repository.update.side_effect = IntegrityError(None, None, None)

        with (
            patch(
                "app.services.variable_set.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_set.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueConflictError) as cm:
                await set_variable(session, user, data, path)

        repository.update.assert_awaited_once_with(variable)
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

        self.assertEqual(variable.variable_value, "new-value")
        self.assertEqual(variable.updated_by, 456)

        error = cm.exception

        self.assertEqual(error.loc, ("body", "variable_key"))
        self.assertEqual(error.error_type, "value_conflict")
        self.assertEqual(error.input_value, "theme")
