from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from app.schemas.lock_retrieve_schema import LockRetrieveResponse
from app.hook import Hook, HOOK_AFTER_LOCK_RETRIEVE
from app.helpers.lock_helper import lock_exists
from app.postgres import get_session
from app.redis import get_cache

router = APIRouter()


@router.get("/lock", summary="Retrieve a lock status.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=LockRetrieveResponse,
            tags=["Lock"])
async def lock_retrieve(
    request: Request, session=Depends(get_session), cache=Depends(get_cache)
) -> LockRetrieveResponse:
    """
    Retrieves a lock status. It checks if the app is locked, preventing
    further operations. This endpoint allows to determine whether the
    app is in a locked state.

    **Auth:**
    - No authentication required.

    **Returns:**
    - `LockRetrieveResponse`: Response on success.

    **Responses:**
    - `200 OK`: Successfully retrieves the lock status.
    - `403 Forbidden`: If the secret key is missing.
    - `423 Locked`: If the app is already locked.

    **Hooks:**
    - `HOOK_AFTER_LOCK_RETRIEVE`: Executes after the lock status is
    successfully retrieved.
    """
    locked = await lock_exists()

    hook = Hook(request.app, session, cache)
    await hook.call(HOOK_AFTER_LOCK_RETRIEVE, locked)

    return {"lock_exists": locked}
