# tests/routers/test_folder_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.user import User
from app.schemas.folder_list import FolderListRequest


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.folder_list import folder_root_list_router  # noqa: E402


class TestFolderListRouter(unittest.IsolatedAsyncioTestCase):

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
                display_name="List Router Creator",
            ),
            folder_updated_by_user=None,
        )
        base.update(kwargs)
        return SimpleNamespace(**base)

    async def test_returns_root_folders(self):
        session = AsyncMock()
        params = FolderListRequest()
        current_user = MagicMock(spec=User)

        folder = self._folder_stub(
            id=1,
            parent_id=None,
            dirname="documents",
            children_count=4,
            files_count=2,
        )

        with patch(
            "app.routers.folder_list.list_folders",
            new_callable=AsyncMock,
            return_value=([folder], 1, False),
        ) as mock_service:
            out = await folder_root_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            params=params,
        )
        self.assertEqual(out.folders_count, 1)
        self.assertEqual(len(out.folders), 1)
        self.assertEqual(out.folders[0].folder_id, 1)
        self.assertEqual(out.folders[0].dirname, "documents")
        self.assertEqual(out.folders[0].created_by.user_id, 100)
        self.assertEqual(
            out.folders[0].created_by.display_name,
            "List Router Creator",
        )
        self.assertIsNone(out.folders[0].updated_by)
        self.assertFalse(out.folders[0].is_write_protected)
        self.assertFalse(out.folders[0].is_write_protected_recursive)
        self.assertEqual(out.folders[0].children_count, 4)
        self.assertEqual(out.folders[0].files_count, 2)

    async def test_returns_root_folder_with_own_recursive_protection(self):
        session = AsyncMock()
        params = FolderListRequest()
        current_user = MagicMock(spec=User)

        folder = self._folder_stub(
            id=2,
            parent_id=None,
            updated_at=200,
            dirname="private",
            is_write_protected=True,
            summary="Private root folder.",
            folder_updated_by_user=SimpleNamespace(
                id=200,
                display_name="List Router Editor",
            ),
        )

        with patch(
            "app.routers.folder_list.list_folders",
            new_callable=AsyncMock,
            return_value=([folder], 1, False),
        ):
            out = await folder_root_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        self.assertTrue(out.folders[0].is_write_protected)
        self.assertFalse(out.folders[0].is_write_protected_recursive)
        self.assertEqual(out.folders[0].updated_by.user_id, 200)

    async def test_returns_child_folders_with_inherited_protection(self):
        session = AsyncMock()
        params = FolderListRequest(
            order_by="created_at",
            order="desc",
            parent_id__eq=1,
        )
        current_user = MagicMock(spec=User)

        folder = self._folder_stub(
            id=3,
            parent_id=1,
            dirname="child",
        )

        with patch(
            "app.routers.folder_list.list_folders",
            new_callable=AsyncMock,
            return_value=([folder], 1, True),
        ) as mock_service:
            out = await folder_root_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            params=params,
        )
        self.assertEqual(out.folders_count, 1)
        self.assertEqual(out.folders[0].folder_id, 3)
        self.assertEqual(out.folders[0].parent_id, 1)
        self.assertFalse(out.folders[0].is_write_protected)
        self.assertTrue(out.folders[0].is_write_protected_recursive)

    async def test_returns_empty_folder_list(self):
        session = AsyncMock()
        params = FolderListRequest()
        current_user = MagicMock(spec=User)

        with patch(
            "app.routers.folder_list.list_folders",
            new_callable=AsyncMock,
            return_value=([], 0, False),
        ) as mock_service:
            out = await folder_root_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            params=params,
        )
        self.assertEqual(out.folders, [])
        self.assertEqual(out.folders_count, 0)
