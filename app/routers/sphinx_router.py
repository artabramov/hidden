from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/sphinx", include_in_schema=False)
async def redirect_to_sphinx(request: Request):
    return RedirectResponse(url=str(request.url) + "/")
