# app/validators/validation_errors.py
# SPDX-License-Identifier: GPL-3.0-only

# NOTE (ADR-23): Validation errors are defined as shared types.
# This ensures consistent 422 responses across validators.

VALUE_MISSING_UPPERCASE = (
    "value_missing_uppercase",
    "Value must contain at least one uppercase letter",
)

VALUE_MISSING_LOWERCASE = (
    "value_missing_lowercase",
    "Value must contain at least one lowercase letter",
)

VALUE_MISSING_DIGIT = (
    "value_missing_digit",
    "Value must contain at least one digit",
)

VALUE_TOO_COMMON = (
    "value_too_common",
    "Value contains a too common or predictable sequence",
)

VALUE_NOT_LATIN_EXTENDED = (
    "value_not_latin_extended",
    "Value must contain only latin letters, digits, underscores, "
    "and hyphens",
)

VALUE_NOT_ALPHANUMERIC_EXTENDED = (
    "value_not_alphanumeric_extended",
    "Value must contain only letters and digits, underscores,"
    "and hyphens",
)

VALUE_NOT_PATH_SEGMENT = (
    "value_not_path_segment",
    "Value must be a single safe filesystem path segment",
)
