import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.partner_model import Partner
from app.schemas.partner_schemas import EmblemUploadResponse
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


@router.post("/partner/{partner_id}/emblem", summary="Upload emblem image",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=EmblemUploadResponse, tags=["Partners"])
@locked
async def emblem_upload(
    partner_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> EmblemUploadResponse:
    partner_repository = Repository(session, cache, Partner)
    partner = await partner_repository.select(id=partner_id)

    if not partner:
        raise E([LOC_PATH, "partner_id"], partner_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif file.content_type not in cfg.EMBLEM_MIMES:
        raise E([LOC_BODY, "file"], partner_id,
                ERR_MIMETYPE_UNSUPPORTED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    if partner.emblem_filename:
        await FileManager.delete(partner.emblem_path)

    emblem_filename = str(uuid.uuid4()) + cfg.EMBLEM_EXTENSION
    emblem_path = os.path.join(cfg.EMBLEM_BASE_PATH, emblem_filename)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_EMBLEM_UPLOAD, partner)

    await FileManager.upload(file, emblem_path)
    await image_resize(emblem_path, cfg.EMBLEM_WIDTH, cfg.EMBLEM_HEIGHT,
                       cfg.EMBLEM_QUALITY)

    partner.emblem_filename = emblem_filename
    await partner_repository.update(partner, commit=False)

    await partner_repository.commit()
    await hook.do(HOOK_AFTER_EMBLEM_UPLOAD, partner)

    return {"partner_id": partner.id}
