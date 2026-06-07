# tests/services/test_user_token_invalidate.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.events import Events as E
from app.models.user import User
from app.services.user_token_invalidate import invalidate_token


class TestInvalidateToken(unittest.IsolatedAsyncioTestCase):
    async def test_invalidates_token_and_updates_user(self):
        session = AsyncMock()

        user = MagicMock(spec=User)
        user.current_jti_encrypted = "old-jti"

        repository = AsyncMock()

        with (
            patch(
                "app.services.user_token_invalidate.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_invalidate.generate_jti",
                return_value="new-jti",
            ) as generate_jti_mock,
            patch(
                "app.services.user_token_invalidate.encrypt_string",
                return_value="encrypted-new-jti",
            ) as encrypt_mock,
            patch(
                "app.services.user_token_invalidate.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_token_invalidate.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await invalidate_token(session, user)

        generate_jti_mock.assert_called_once_with()
        encrypt_mock.assert_called_once_with("new-jti")

        self.assertEqual(user.current_jti_encrypted, "encrypted-new-jti")

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.USER_TOKEN_INVALIDATE_COMPLETED,
            session,
            user,
        )
