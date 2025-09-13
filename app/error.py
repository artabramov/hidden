"""
Centralized error definitions and HTTPException wrapper ensuring
consistent error codes and unified response format across the API.
"""

from fastapi import HTTPException

# Custom HTTP error codes
HTTP_498_SECRET_KEY_MISSING = 498
HTTP_499_SECRET_KEY_INVALID = 499

# Locations
LOC_HEADER = "header"
LOC_COOKIE = "cookie"
LOC_PATH = "path"
LOC_QUERY = "query"
LOC_BODY = "body"

# 401
ERR_TOKEN_MISSING   = "token_missing"
ERR_TOKEN_INVALID   = "token_invalid"
ERR_TOKEN_EXPIRED   = "token_expired"

# 403/422
ERR_USER_NOT_FOUND  = "user_not_found"
ERR_USER_SUSPENDED = "user_suspended"
ERR_USER_INACTIVE = "user_inactive"
ERR_USER_REJECTED = "user_rejected"
ERR_ROLE_FORBIDDEN = "role_forbidden"
ERR_USER_NOT_LOGGED_IN = "user_not_logged_in"

# 404/422
ERR_VALUE_NOT_FOUND = "value_not_found"
ERR_VALUE_EXISTS = "value_exists"
ERR_VALUE_EMPTY = "value_empty"
ERR_VALUE_INVALID = "value_invalid"

# 404/422
ERR_FILE_NOT_FOUND = "file_not_found"
ERR_FILE_MIMETYPE_INVALID = "file_mimetype_invalid"
ERR_FILE_CHECKSUM_MATCHED = "file_checksum_matched"
ERR_FILE_WRITE_ERROR = "file_write_error"
ERR_FILE_HASH_MISMATCH  = "file_hash_mismatch"

# 423/498/499/500
ERR_LOCKED = "locked"
ERR_SECRET_KEY_MISSING = "secret_key_missing"
ERR_SECRET_KEY_INVALID = "secret_key_invalid"
ERR_SERVER_ERROR = "server_error"


class E(HTTPException):
    """
    Unified HTTPException wrapper that produces error details in the
    same shape as Pydantic validation errors.
    """

    def __init__(self, loc: list, error_input: str, error_type: str,
                 status_code: int):
        detail = [{"loc": loc, "input": error_input, "type": error_type}]
        super().__init__(status_code=status_code, detail=detail)
