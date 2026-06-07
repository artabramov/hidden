# tests/routers/test_folder_select.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.user import User


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.folder_select import folder_select_router  # noqa: E402


class TestFolderSelectRouter(unittest.IsolatedAsyncioTestCase):

    def _folder_stub(self, **kwargs):
        base = dict(
            created_at=100,
            updated_at=None,
            dirname="documents",
            is_write_protected=False,
            children_count=0,
            files_count=0,
            summary=None,
            folder_created_by_user=SimpleNamespace(
                id=100,
                display_name="Router Creator",
            ),
            folder_updated_by_user=None,
        )
        base.update(kwargs)
        return SimpleNamespace(**base)

    async def test_returns_folder(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        folder = self._folder_stub(
            id=1,
            parent_id=None,
            dirname="documents",
            children_count=2,
            files_count=3,
        )

        with patch(
            "app.routers.folder_select.select_folder",
            new_callable=AsyncMock,
            return_value=(folder, False),
        ) as mock_service:
            out = await folder_select_router(
                folder_id=1,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            folder_id=1,
        )
        self.assertEqual(out.folder_id, 1)
        self.assertIsNone(out.parent_id)
        self.assertEqual(out.created_at, 100)
        self.assertEqual(out.created_by.user_id, 100)
        self.assertEqual(out.created_by.display_name, "Router Creator")
        self.assertIsNone(out.updated_at)
        self.assertIsNone(out.updated_by)
        self.assertEqual(out.dirname, "documents")
        self.assertFalse(out.is_write_protected)
        self.assertFalse(out.is_write_protected_recursive)
        self.assertEqual(out.children_count, 2)
        self.assertEqual(out.files_count, 3)
        self.assertIsNone(out.summary)

    async def test_returns_folder_with_recursive_protection(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        folder = self._folder_stub(
            id=2,
            parent_id=1,
            updated_at=200,
            dirname="private",
            summary="Private folder.",
            folder_updated_by_user=SimpleNamespace(
                id=200,
                display_name="Router Editor",
            ),
        )

        with patch(
            "app.routers.folder_select.select_folder",
            new_callable=AsyncMock,
            return_value=(folder, True),
        ):
            out = await folder_select_router(
                folder_id=2,
                session=session,
                current_user=current_user,
            )

        self.assertEqual(out.folder_id, 2)
        self.assertEqual(out.parent_id, 1)
        self.assertEqual(out.updated_at, 200)
        self.assertEqual(out.updated_by.user_id, 200)
        self.assertEqual(out.updated_by.display_name, "Router Editor")
        self.assertFalse(out.is_write_protected)
        self.assertTrue(out.is_write_protected_recursive)
        self.assertEqual(out.summary, "Private folder.")

    async def test_returns_folder_with_own_protection(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        folder = self._folder_stub(
            id=3,
            parent_id=None,
            dirname="locked",
            is_write_protected=True,
        )

        with patch(
            "app.routers.folder_select.select_folder",
            new_callable=AsyncMock,
            return_value=(folder, True),
        ):
            out = await folder_select_router(
                folder_id=3,
                session=session,
                current_user=current_user,
            )

        self.assertTrue(out.is_write_protected)
        self.assertTrue(out.is_write_protected_recursive)
