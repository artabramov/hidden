# app.validators package

## app.validators.file_validators module

Cross-platform validators for names and summaries used in a file storage
context. The name checker normalizes Unicode, trims whitespace, rejects
special path components, filters out control and portability-breaking
characters, forbids trailing dots and platform-reserved basenames, and
enforces a 255-byte UTF-8 limit to match common filesystem constraints.
The summary helper applies a minimal normalization pass that strips
surrounding whitespace and converts empty strings to null, ensuring
consistent optional metadata handling.

### app.validators.file_validators.name_validate(name: str) → str

Validates name used as a single component by trimming surrounding
whitespace and ensuring the result is not empty, rejecting the
special components ‘.’ and ‘..’, forbidding characters that are
problematic across platforms as well as any ASCII control characters
including NUL, disallowing a trailing dot and Windows-reserved names
regardless of extension, and enforcing a maximum of 255 bytes when
encoded in UTF-8. The value is Unicode-normalized to NFC prior to
the byte-length check, and the normalized name is returned.

### app.validators.file_validators.summary_validate(summary: str | None) → str | None

Validates file summary by trimming whitespace and converting
blank strings to None. Returns the normalized file summary.

## app.validators.folder_validators module

Validators for folder metadata. Provides a simple normalization pass for
textual summaries that trims surrounding whitespace and converts blank
input to a null value.

### app.validators.folder_validators.summary_validate(summary: str | None) → str | None

Validates summary by trimming whitespace and converting blank
strings to None. Returns the normalized summary.

## app.validators.tag_validators module

Validator for free-form tag values that enforces a canonical,
search-friendly representation. Input is Unicode-normalized,
whitespace is trimmed, and case is folded to achieve consistent
comparisons across locales. Blank or purely whitespace input is
rejected to prevent meaningless records.

### app.validators.tag_validators.value_validate(value: str) → str

Normalize to NFKC, trim, and lower-case; reject empty.

## app.validators.user_validators module

Validators for user input in authentication and profiles: lowercases
and restricts usernames to letters, digits, and underscores; enforces
passwords with mixed case, digits, and punctuation while forbidding
spaces; trims and lowercases roles without asserting membership; accepts
digit-only TOTP codes; and normalizes summaries by stripping whitespace
and collapsing blanks to null.

### app.validators.user_validators.password_validate(password: str) → str

Validates password by disallowing spaces and requiring lowercase,
uppercase, digit, and special character.

### app.validators.user_validators.role_validate(role: str) → str

Normalizes a role string without validating membership. Strips
leading/trailing whitespace and lowercases the value.

### app.validators.user_validators.summary_validate(summary: str | None) → str | None

Validates summary by trimming whitespace and converting blank
strings to None.

### app.validators.user_validators.totp_validate(totp: str)

The one-time password must contain only digits.

### app.validators.user_validators.username_validate(username: str) → str

Validates username by lowercasing and ensuring only lowercase
letters, digits, or underscore are allowed.

## Module contents
