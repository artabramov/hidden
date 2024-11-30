from fastapi import APIRouter, Depends, Response, status
from app.database import get_session
from app.cache import get_cache
from app.repository import Repository
import qrcode
from io import BytesIO
from app.config import get_config
from app.decorators.locked_decorator import locked
from app.models.user_model import User
from app.errors import E
from app.hooks import Hook
from app.constants import (
    LOC_QUERY, ERR_RESOURCE_FORBIDDEN, ERR_VALUE_INVALID,
    HOOK_BEFORE_MFA_SELECT, HOOK_AFTER_MFA_SELECT)

router = APIRouter()
cfg = get_config()

MFA_MASK = "otpauth://totp/%s?secret=%s&issuer=%s"


@router.get("/user/{user_id}/mfa/{mfa_secret}", summary="Retrieve MFA",
            status_code=status.HTTP_200_OK, include_in_schema=True,
            tags=["Users"])
@locked
async def user_mfa(
    user_id: int, mfa_secret: str,
    session=Depends(get_session), cache=Depends(get_cache)
):
    """
    Retrieve a QR code for MFA setup for a user. This endpoint validates
    the user's MFA secret and generates a QR code that can be scanned by
    an MFA app. The QR code includes the MFA secret and user login
    information.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_QUERY, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif user.is_active:
        raise E([LOC_QUERY, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    elif user.mfa_secret != mfa_secret:
        raise E([LOC_QUERY, "mfa_secret"], mfa_secret,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    hook = Hook(session, cache)
    await hook.do(HOOK_BEFORE_MFA_SELECT, user)

    qr = qrcode.QRCode(
        version=cfg.MFA_VERSION, box_size=cfg.MFA_BOX_SIZE,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        border=cfg.MFA_BORDER
        )
    qr.add_data(MFA_MASK % (cfg.MFA_APP_NAME, user.mfa_secret,
                            user.user_login))
    qr.make(fit=cfg.MFA_FIT)

    img = qr.make_image(fill_color=cfg.MFA_COLOR,
                        back_color=cfg.MFA_BACKGROUND)

    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)
    img_data = img_bytes.getvalue()

    await hook.do(HOOK_AFTER_MFA_SELECT, user)

    return Response(content=img_data, media_type=cfg.MFA_MIMETYPE)
