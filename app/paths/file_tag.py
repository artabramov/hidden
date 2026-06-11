# app/paths/file_tag.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import HTTPException, Path, status
from pydantic import ValidationError

from app.schemas.file_tag_path import FileTagPath


def get_file_tag_path(
    file_id: int = Path(
        ...,
        description="ID of the target file.",
    ),
    tag: str = Path(
        ...,
        description="Tag value attached to the file.",
    ),
) -> FileTagPath:
    """Build and validate path parameters for file tag routes."""
    try:
        return FileTagPath.model_validate(
            {"file_id": file_id, "tag": tag},
        )

    except ValidationError as exc:
        errors = []

        for err in exc.errors():
            errors.append({
                "type": err["type"],
                "loc": ["path", *err["loc"]],
                "msg": err["msg"],
                "input": err.get("input"),
            })

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors,
        ) from exc
