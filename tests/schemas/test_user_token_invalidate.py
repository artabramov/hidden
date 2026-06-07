# tests/schemas/test_user_token_invalidate.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from app.schemas.user_token_invalidate import USER_TOKEN_INVALIDATE_ERRORS


class TestUserTokenInvalidateErrors(unittest.TestCase):

    def test_declares_expected_status_codes(self):
        self.assertEqual(
            set(USER_TOKEN_INVALIDATE_ERRORS),
            {401, 403, 503},
        )
