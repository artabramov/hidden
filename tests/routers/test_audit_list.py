# tests/routers/test_audit_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.events import Events as E
from app.models.user import User
from app.schemas.audit_list import AuditListRequest


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.audit_list import audit_list_router  # noqa: E402


class TestAuditListRouter(unittest.IsolatedAsyncioTestCase):
    async def test_returns_audit_page_and_service_log_is_emitted(self):
        session = AsyncMock()
        params = AuditListRequest()
        current_user = MagicMock(spec=User)

        row = SimpleNamespace(
            id=7,
            created_at=1_700_000_000,
            created_by=1,
            event="user_login:succeeded",
            request_uuid="uuid-1",
            resource_type="users",
            resource_id=1,
        )

        repository = AsyncMock()
        repository.count_all = AsyncMock(return_value=1)
        repository.select_all = AsyncMock(return_value=[row])

        with (
            patch(
                "app.services.audit_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.audit_list.hooks.emit",
                new_callable=AsyncMock,
            ),
            self.assertLogs("app.services.audit_list", level="INFO") as log_cm,
        ):
            out = await audit_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        self.assertEqual(out.audit_count, 1)
        self.assertEqual(len(out.audit), 1)
        self.assertEqual(out.audit[0].audit_id, 7)
        self.assertEqual(out.audit[0].event, "user_login:succeeded")
        self.assertTrue(
            any(
                E.AUDIT_LIST_COMPLETED in entry
                for entry in log_cm.output
            ),
            msg=log_cm.output,
        )
