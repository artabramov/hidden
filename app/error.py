"""
Defines a custom HTTP exception class with extended error details such
as location, input, type, and status code, along with common error
identifiers used across the app.
"""

from fastapi import HTTPException

LOC_HEADER = "header"
LOC_COOKIE = "cookie"
LOC_PATH = "path"
LOC_QUERY = "query"
LOC_BODY = "body"

ERR_SERVER_FORBIDDEN = "server_forbidden"
ERR_SERVER_LOCKED = "server_locked"
ERR_SERVER_ERROR = "server_error"

ERR_TOKEN_INVALID = "token_invalid"
ERR_TOKEN_EXPIRED = "token_expired"
ERR_TOKEN_REJECTED = "token_rejected"

ERR_USER_NOT_LOGGED_IN = "user_not_logged_in"
ERR_USER_NOT_FOUND = "user_not_found"
ERR_USER_SUSPENDED = "user_suspended"
ERR_USER_INACTIVE = "user_inactive"

ERR_VALUE_NOT_FOUND = "value_not_found"
ERR_VALUE_EXISTS = "value_exists"
ERR_VALUE_EMPTY = "value_empty"
ERR_VALUE_ERROR = "value_error"

ERR_FILE_NOT_FOUND = "file_not_found"
ERR_FILE_ERROR = "file_error"


class E(HTTPException):
    """
    Custom HTTP exception that extends FastAPI's HTTPException with
    structured details including error location, input value, error
    type, and status code for consistent API error responses.
    """

    def __init__(self, loc: list, error_input: str, error_type: str,
                 status_code: int):
        """
        Initializes the exception with the provided error location,
        input value, error type, and HTTP status code, storing details
        in a format compatible with FastAPI validation-style error
        responses.
        """
        detail = [{"loc": loc, "input": error_input, "type": error_type}]
        super().__init__(status_code=status_code, detail=detail)
