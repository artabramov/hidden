# app/schemas/folder_select.py
# SPDX-License-Identifier: GPL-3.0-only

from types import SimpleNamespace

from pydantic import BaseModel, ConfigDict, Field

from app.models.folder import Folder
from app.schemas.pydantic_error import PydanticErrorResponse

FOLDER_SELECT_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Authenticated user is inactive, blocked, or lacks "
            "required permissions."
        ),
    },
    404: {
        "description": "Target folder was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (e.g. non-integer folder ID "
            "in the path)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FolderSelectUserResponse(BaseModel):
    """
    Response schema for user reference.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    user_id: int = Field(
        validation_alias="id",
        description="Identifier of the user.",
    )

    display_name: str = Field(
        description="Display name of the user.",
    )


class FolderSelectResponse(BaseModel):
    """
    Response schema for folder selection containing folder metadata,
    user references, hierarchy information, write-protection state,
    and summary.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    folder_id: int = Field(
        validation_alias="id",
        description="Identifier of the folder.",
    )

    parent_id: int | None = Field(
        default=None,
        description="Identifier of the parent folder. Null means the root.",
    )

    created_at: int = Field(
        description="Timestamp when the folder was created.",
    )

    created_by: FolderSelectUserResponse = Field(
        description="User who created the folder.",
    )

    updated_at: int | None = Field(
        default=None,
        description="Timestamp when the folder was last updated.",
    )

    updated_by: FolderSelectUserResponse | None = Field(
        default=None,
        description="User who last updated the folder.",
    )

    dirname: str = Field(
        description="Folder directory name.",
    )

    is_write_protected: bool = Field(
        description="Whether this folder is explicitly write-protected.",
    )

    is_write_protected_recursive: bool = Field(
        description=(
            "Whether this folder is write-protected directly or through "
            "one of its parent folders."
        ),
    )

    children_count: int = Field(
        ge=0,
        description=(
            "Number of direct child folders, sourced from the folder's "
            "denormalized counter. Useful for tree-view UIs to determine "
            "whether the node is expandable without an extra request."
        ),
    )

    files_count: int = Field(
        ge=0,
        description=(
            "Number of direct files inside the folder, sourced from the "
            "folder's denormalized counter."
        ),
    )

    summary: str | None = Field(
        default=None,
        description="Optional folder summary.",
    )


def build_folder_response(
    folder: Folder,
    is_write_protected_recursive: bool,
) -> FolderSelectResponse:
    """
    Build folder response with recursive write-protection state.
    """
    return FolderSelectResponse.model_validate(
        SimpleNamespace(
            id=folder.id,
            parent_id=folder.parent_id,
            created_by=SimpleNamespace(
                id=folder.folder_created_by_user.id,
                display_name=folder.folder_created_by_user.display_name,
            ),
            created_at=folder.created_at,
            updated_by=(
                SimpleNamespace(
                    id=folder.folder_updated_by_user.id,
                    display_name=folder.folder_updated_by_user.display_name,
                )
                if folder.folder_updated_by_user is not None
                else None
            ),
            updated_at=folder.updated_at,
            dirname=folder.dirname,
            is_write_protected=folder.is_write_protected,
            is_write_protected_recursive=is_write_protected_recursive,
            children_count=folder.children_count,
            files_count=folder.files_count,
            summary=folder.summary,
        )
    )
