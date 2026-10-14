# app/errors.py
# SPDX-License-Identifier: Apache-2.0


class UnauthorizedError(Exception):
    """Raised when credentials are invalid (401)."""
    pass


class InternalServerError(Exception):
    """Raised when an unexpected internal error occurs (500)."""
    pass


class BadGatewayError(Exception):
    """Raised when infrastructure is in a conflicting state (502)."""
    pass


class ServiceUnavailableError(Exception):
    """Raised when the cipherdir or secrets are unavailable (503)."""
    pass
