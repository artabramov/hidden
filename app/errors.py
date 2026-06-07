# app/errors.py
# SPDX-License-Identifier: SSPL-1.0

# TODO: Review broad exception handling and narrow exception types where
# appropriate (encryption/decryption, master password handling, mount
# lifecycle, subprocess execution, filesystem operations, watchdog
# checks, and service-layer exception mapping).


class InternalServerError(Exception):
    """Raised when an unexpected internal error occurs (500)."""
    pass


class ServiceUnavailableError(Exception):
    """Raised when the service is temporarily unavailable (503)."""
    pass


class ResourceNotFoundError(Exception):
    """Resource with given ID does not exist (404)."""
    pass


class ResourceForbiddenError(Exception):
    """Access to the requested resource is forbidden (403)."""
    pass


class ResourceConflictError(Exception):
    """Operation conflicts with current resource state (409)."""
    pass


class ResourceLockedError(Exception):
    """The resource that is being accessed is locked (423)."""
    pass


class TooManyRequestsError(Exception):
    """Raised when request rate exceeds allowed limits (429)."""
    pass


# NOTE (ADR-33): Errors are split into resource and field-level types.
# 1. Standard HTTP codes (404, 403, etc.) are used for resource
#    identification, access control, and system state.
# 2. Errors related to specific request fields (body or query) are
#    returned as 422, allowing direct mapping to client inputs.

class PydanticError(Exception):
    """
    Base class for 422 errors represented in a Pydantic-like format.
    Not related to Pydantic exceptions themselves; used as the project's
    unified validation error container.
    """

    def __init__(
        self,
        *,
        scope: str,
        field: str,
        error_type: str,
        message: str,
        input_value: object | None = None,
    ) -> None:
        self.loc = (scope, field)
        self.error_type = error_type
        self.message = message
        self.input_value = input_value

    @property
    def detail(self) -> list[dict]:
        return [{
            "type": self.error_type,
            "loc": list(self.loc),
            "msg": self.message,
            "input": self.input_value,
        }]


class ValueInvalidError(PydanticError):
    """
    Raised when a value is invalid according to application logic.
    Produces a generic 422 error without detailed validation info.
    """

    def __init__(
        self,
        *,
        field: str,
        input_value: object | None = None,
    ) -> None:
        super().__init__(
            scope="body",
            field=field,
            error_type="value_invalid",
            message="The value is invalid",
            input_value=input_value,
        )


class ValueNotFoundError(PydanticError):
    """
    Raised when a referenced value does not exist.
    Produces a generic 422 error without detailed validation info.
    """

    def __init__(
        self,
        *,
        field: str,
        input_value: object | None = None,
    ) -> None:
        super().__init__(
            scope="body",
            field=field,
            error_type="value_not_found",
            message="The value was not found",
            input_value=input_value,
        )


class ValueConflictError(PydanticError):
    """
    Raised when a value conflicts with existing data.
    Produces a generic 422 error without detailed validation info.
    """

    def __init__(
        self,
        *,
        field: str,
        input_value: object | None = None,
    ) -> None:
        super().__init__(
            scope="body",
            field=field,
            error_type="value_conflict",
            message="The value conflicts with existing data",
            input_value=input_value,
        )


class ValueAuthenticationError(PydanticError):
    """
    Raised when an authentication step fails within the login or
    token issuance flow.

    Covers all failure cases at these stages, including non-existent
    user, invalid credentials, inactive or suspended account, and
    invalid TOTP code.

    Returned as a field-level 422 error bound to the username field
    without revealing the exact reason for the failure.
    """

    def __init__(
        self,
        *,
        field: str,
        input_value: object | None = None,
    ) -> None:
        super().__init__(
            scope="body",
            field=field,
            error_type="value_authentication",
            message="Authentication failed",
            input_value=input_value,
        )
