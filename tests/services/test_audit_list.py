# tests/services/test_audit_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.events import Events as E  # noqa: E402
from app.models.audit import Audit  # noqa: E402
from app.schemas.audit_list import AuditListRequest  # noqa: E402
from app.services.audit_list import list_audit  # noqa: E402


class TestListAudit(unittest.IsolatedAsyncioTestCase):
    async def test_logs_audit_list_succeeded_after_fetch(self):
        session = AsyncMock()
        params = AuditListRequest()

        repository = AsyncMock()
        repository.count_all = AsyncMock(return_value=0)
        repository.select_all = AsyncMock(return_value=[])

        with (
            patch(
                "app.services.audit_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.audit_list.hooks.emit",
                new_callable=AsyncMock,
            ) as emit_mock,
            self.assertLogs("app.services.audit_list", level="INFO") as log_cm,
        ):
            audit, audit_count = await list_audit(session, params)

        self.assertEqual(audit, [])
        self.assertEqual(audit_count, 0)
        emit_mock.assert_awaited_once_with(
            E.AUDIT_LIST_COMPLETED,
            session,
            audit,
        )
        self.assertTrue(
            any(
                E.AUDIT_LIST_COMPLETED in entry
                for entry in log_cm.output
            ),
            msg=log_cm.output,
        )

    async def test_wraps_event_ilike_filter_before_repository_calls(self):
        session = AsyncMock()
        params = AuditListRequest(event__ilike="login")

        repository = AsyncMock()
        repository.count_all = AsyncMock(return_value=1)
        repository.select_all = AsyncMock(return_value=[])

        with (
            patch(
                "app.services.audit_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.audit_list.hooks.emit",
                new_callable=AsyncMock,
            ),
            self.assertLogs("app.services.audit_list", level="INFO"),
        ):
            await list_audit(session, params)

        expected_filters = params.model_dump(exclude_none=True)
        expected_filters["event__ilike"] = "%login%"

        repository.count_all.assert_awaited_once_with(
            Audit,
            **expected_filters,
        )
        repository.select_all.assert_awaited_once_with(
            Audit,
            **expected_filters,
        )
