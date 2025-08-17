"""
The module defines Pydantic schemas for retrieving a secret key.
"""

from pydantic import BaseModel


class SecretRetrieveResponse(BaseModel):
    """
    Response schema for retrieving a secret key information. Contains
    the secret key and the secret path, which are provided after
    successfully retrieving the user's secret.
    """
    created_date: int
    secret_key: str
    secret_path: str
