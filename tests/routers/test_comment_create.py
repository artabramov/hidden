# tests/routers/test_comment_create.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.comment_create import comment_create_router  # noqa: E402
from app.schemas.comment_create import CommentCreateRequest  # noqa: E402


class TestCommentCreateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_comment_create_response(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        data = CommentCreateRequest(body="Comment body.")

        comment = MagicMock()
        comment.id = 42

        with patch(
            "app.routers.comment_create.create_comment",
            new_callable=AsyncMock,
            return_value=comment,
        ) as mock_service:
            result = await comment_create_router(
                file_id=7,
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            file_id=7,
            data=data,
        )

        self.assertEqual(result.comment_id, 42)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
