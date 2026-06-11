# app/security/cipherdir.py
# SPDX-License-Identifier: GPL-3.0-only

# NOTE (ADR-15): Master-password checks use entropy and crypto cost.
# 1. Scope is online guessing against endpoints that verify the master
#    password. Compromise of persisted ciphertext (encrypted passphrase)
#    and offline cracking are a separate threat model and not addressed
#    here.
# 2. Primary defense is master-password policy (minimum length and
#    related validation), which keeps the guessing space astronomically
#    large for typical operator-chosen secrets.
# 3. Each failed verification still pays full cryptographic cost
#    (decrypt attempt), which slows automated guessing beyond wall-clock
#    spacing alone.

# NOTE (ADR-16): Master-password attempt throttling is per-process.
# 1. Shared gate: is_master_password_attempt_throttled; callers map True
#    to HTTP 429 (TooManyRequestsError).
# 2. Verifying services call the gate before passphrase checks;
#    create_cipherdir does not use it.

import asyncio
import time

from app.constants import MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS

_gate_lock = asyncio.Lock()
_last_attempt_monotonic: float = 0.0


def _monotonic() -> float:
    """Monotonic clock for rate limiting; patched in unit tests only."""
    return time.monotonic()


async def is_master_password_attempt_throttled() -> bool:
    """
    Per-process spacing for master-password verification attempts.

    Returns True if this call is still inside the minimum interval since
    the last registered attempt (timestamp unchanged); callers should
    treat this as HTTP 429 (e.g. raise TooManyRequestsError).
    Returns False if the attempt may proceed; updates the timestamp
    before password verification so failed attempts count toward the
    limit. Despite the ``is_`` prefix, the False branch has this side
    effect by design.
    """
    global _last_attempt_monotonic

    async with _gate_lock:
        now = _monotonic()
        if _last_attempt_monotonic > 0.0:
            elapsed = now - _last_attempt_monotonic
            if elapsed < MASTER_PASSWORD_ATTEMPT_MIN_INTERVAL_SECONDS:
                return True
        _last_attempt_monotonic = now
        return False
