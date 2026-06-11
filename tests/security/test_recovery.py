# tests/security/test_recovery.py
# SPDX-License-Identifier: GPL-3.0-only

import re
import string
import unittest
from unittest.mock import patch

from app.security import recovery


class TestRecovery(unittest.TestCase):
    # Uppercase + digits without 0, O, 1, I — six XXXX segments.
    _PATTERN = re.compile(
        r"^[A-HJ-NP-Z2-9]{4}(-[A-HJ-NP-Z2-9]{4}){5}$"
    )

    def test_layout_constants_match_generated_segments(self):
        code = recovery.generate_recovery_code()
        parts = code.split("-")
        self.assertEqual(
            len(parts),
            recovery.RECOVERY_CODE_SEGMENT_COUNT,
        )
        for part in parts:
            self.assertEqual(
                len(part),
                recovery.RECOVERY_CODE_SEGMENT_LEN,
            )

    def test_generate_recovery_code_matches_format(self):
        code = recovery.generate_recovery_code()

        self.assertIsInstance(code, str)
        self.assertRegex(code, self._PATTERN)
        self.assertEqual(len(code), 29)

    def test_generate_recovery_code_uses_human_facing_alphabet(self):
        code = recovery.generate_recovery_code()
        allowed = "".join(
            c
            for c in string.ascii_uppercase + string.digits
            if c not in "01IO"
        )

        for ch in code:
            if ch != "-":
                self.assertIn(ch, allowed)

    def test_generate_recovery_code_returns_different_values(self):
        c1 = recovery.generate_recovery_code()
        c2 = recovery.generate_recovery_code()

        self.assertNotEqual(c1, c2)

    def test_generate_recovery_code_joins_groups_with_hyphens(self):
        with patch.object(
            recovery.secrets,
            "choice",
            side_effect=list("WXYZ" * 6),
        ):
            code = recovery.generate_recovery_code()

        self.assertEqual(
            code,
            "WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
        )
