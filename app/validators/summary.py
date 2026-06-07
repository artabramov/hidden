# app/validators/summary.py
# SPDX-License-Identifier: SSPL-1.0

def normalize_summary(value: str | None) -> str | None:
    if value == "":
        return None
    return value
