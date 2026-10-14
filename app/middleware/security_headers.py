# app/middleware/security_headers.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import Request


async def security_headers_middleware(request: Request, call_next):
    """
    Add security-related response headers that disable MIME type
    sniffing, prevent framing, and suppress referrer information.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
