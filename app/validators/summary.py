# app/validators/summary.py
# SPDX-License-Identifier: GPL-3.0-only

def normalize_summary(value: str | None) -> str | None:
    if value == "":
        return None
    return value
