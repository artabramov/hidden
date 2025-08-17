"""
The module defines Pydantic schemas for changing a user's password.
"""

from pydantic import BaseModel, Field, field_validator
from app.validators.user_password_validator import user_password_validate


class UserPasswordRequest(BaseModel):
    """
    Request schema for updating a user's password. Contains the current
    password and the new password. The updated password must meet
    specific security requirements: it must contain at least one
    lowercase letter, one uppercase letter, one digit, and one special
    character. Both passwords have a minimum length of 6 characters.
    """
    current_password: str = Field(..., min_length=6)
    updated_password: str = Field(..., min_length=6)

    @field_validator("updated_password", mode="before")
    def validate_updated_password(cls, updated_password: str) -> str:
        """
        Password must contain at least one lowercase letter, one
        uppercase letter, one digit, and one special character.
        """
        return user_password_validate(updated_password)


class UserPasswordResponse(BaseModel):
    """
    Response schema for the successful update of a user's password.
    Contains the user's unique identifier that confirms the password
    was updated for the specific user record.
    """
    user_id: int
