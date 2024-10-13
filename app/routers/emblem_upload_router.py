import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.member_model import Member
from app.schemas.member_schemas import EmblemUploadResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.helpers.image_helper import image_resize
from app.config import get_config
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND,
    ERR_MIMETYPE_UNSUPPORTED, HOOK_BEFORE_EMBLEM_UPLOAD,
    HOOK_AFTER_EMBLEM_UPLOAD)

router = APIRouter()
cfg = get_config()


@router.post("/member/{member_id}/emblem", summary="Upload emblem image",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=EmblemUploadResponse, tags=["Members"])
@locked
async def emblem_upload(
    member_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> EmblemUploadResponse:
    member_repository = Repository(session, cache, Member)
    member = await member_repository.select(id=member_id)

    if not member:
        raise E([LOC_PATH, "member_id"], member_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif file.content_type not in cfg.EMBLEM_MIMES:
        raise E([LOC_BODY, "file"], member_id,
                ERR_MIMETYPE_UNSUPPORTED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    if member.emblem_filename:
        await FileManager.delete(member.emblem_path)

    emblem_filename = str(uuid.uuid4()) + cfg.EMBLEM_EXTENSION
    emblem_path = os.path.join(cfg.EMBLEM_BASE_PATH, emblem_filename)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_EMBLEM_UPLOAD, member)

    await FileManager.upload(file, emblem_path)
    await image_resize(emblem_path, cfg.EMBLEM_WIDTH, cfg.EMBLEM_HEIGHT,
                       cfg.EMBLEM_QUALITY)

    member.emblem_filename = emblem_filename
    await member_repository.update(member, commit=False)

    await member_repository.commit()
    await hook.do(HOOK_AFTER_EMBLEM_UPLOAD, member)

    return {"member_id": member.id}
