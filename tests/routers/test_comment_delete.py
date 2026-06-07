# tests/routers/test_comment_delete.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.comment_delete import comment_delete_router  # noqa: E402


class TestCommentDeleteRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_comment_delete_response(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        comment = MagicMock()
        comment.id = 42

        with patch(
            "app.routers.comment_delete.delete_comment",
            new_callable=AsyncMock,
            return_value=comment,
        ) as mock_service:
            result = await comment_delete_router(
                comment_id=7,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            comment_id=7,
        )

        self.assertEqual(result.comment_id, 42)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
