"""
The module provides a custom HTTP exception class E, for detailed
error reporting in the applications. The E class extends HTTPException
to include additional error details such as location, input, type,
and HTTP status code. It defines various error codes for common issues,
including token-related errors, user status problems, resource access
issues, and value validation errors. By using this exception class,
we can deliver more granular and actionable error information in API
responses, aiding both debugging and user experience.
"""

from fastapi import HTTPException


class E(HTTPException):
    """
    Custom HTTP exception class for detailed error reporting, allowing
    specification of error location, input, type and HTTP status code.
    This class helps to provide more granular error information in
    responses, useful for debugging and user experience.
    """
    def __init__(self, loc: list, error_input: str, error_type: str,
                 status_code: int):
        """
        Initializes the exception with detailed error information,
        including the location of the error, the input that caused it,
        the type of the error, and the HTTP status code.
        """
        detail = [{"loc": loc, "input": error_input, "type": error_type}]
        super().__init__(status_code=status_code, detail=detail)
