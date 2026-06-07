# app/security/recovery.py
# SPDX-License-Identifier: SSPL-1.0

import secrets
import string

# Human-facing: exclude 0/O and 1/I.
_EXCLUDED = frozenset("01IO")
_ALPHABET = "".join(
    c for c in string.ascii_uppercase + string.digits if c not in _EXCLUDED
)

RECOVERY_CODE_SEGMENT_LEN = 4
RECOVERY_CODE_SEGMENT_COUNT = 6


def generate_recovery_code() -> str:
    """
    Return a random recovery code: XXXX-XXXX-... (6 groups of 4).

    Uses uppercase letters and digits with 0, O, 1, and I omitted for
    readability.
    """
    groups = [
        "".join(
            secrets.choice(_ALPHABET)
            for _ in range(RECOVERY_CODE_SEGMENT_LEN)
        )
        for _ in range(RECOVERY_CODE_SEGMENT_COUNT)
    ]
    return "-".join(groups)
