# tests/test_audit.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.audit import write_audit
from app.models.audit import Audit


class TestWriteAudit(unittest.IsolatedAsyncioTestCase):

    async def test_writes_audit_event_using_context_user(self):
        repository = MagicMock()
        repository.insert = AsyncMock()

        def get_context_var(name):
            values = {
                "current_user_id": 7,
                "request_uuid": "request-123",
            }
            return values.get(name)

        with (
            patch("app.audit.get_context_var", side_effect=get_context_var),
        ):
            await write_audit(
                repository=repository,
                event="file_delete:completed",
                resource_type="files",
                resource_id=42,
            )

        repository.insert.assert_awaited_once()

        audit_event = repository.insert.await_args.args[0]
        self.assertIsInstance(audit_event, Audit)
        self.assertEqual(audit_event.created_by, 7)
        self.assertEqual(audit_event.event, "file_delete:completed")
        self.assertEqual(audit_event.request_uuid, "request-123")
        self.assertEqual(audit_event.resource_type, "files")
        self.assertEqual(audit_event.resource_id, 42)

        self.assertEqual(
            repository.insert.await_args.kwargs,
            {"commit": False},
        )

    async def test_explicit_user_id_overrides_context_user(self):
        repository = MagicMock()
        repository.insert = AsyncMock()

        with (
            patch("app.audit.get_context_var", return_value="request-123"),
        ):
            await write_audit(
                repository=repository,
                event="user_update:completed",
                current_user_id=9,
                commit=True,
            )

        audit_event = repository.insert.await_args.args[0]
        self.assertEqual(audit_event.created_by, 9)
        self.assertEqual(audit_event.event, "user_update:completed")
        self.assertEqual(audit_event.request_uuid, "request-123")
        self.assertIsNone(audit_event.resource_type)
        self.assertIsNone(audit_event.resource_id)

        self.assertEqual(
            repository.insert.await_args.kwargs,
            {"commit": True},
        )

    async def test_uses_given_repository_instance(self):
        repository = MagicMock()
        repository.insert = AsyncMock()

        with patch("app.audit.get_context_var", return_value=None):
            await write_audit(repository=repository, event="event")

        repository.insert.assert_awaited_once()
