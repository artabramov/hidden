"""
The module defines Pydantic schemas for deleting a secret key.
"""

from pydantic import BaseModel


class SecretDeleteResponse(BaseModel):
    """
    Response schema for the successful deletion of a user's secret.
    Contains the secret path that confirms the deletion of the specific
    secret.
    """
    secret_path: str
