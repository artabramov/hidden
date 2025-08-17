"""
The main module initializes and runs the FastAPI app. It sets up
middleware for logging and context management, handles app startup
tasks, serves static files, manages exceptions, and includes all
API routers.
"""

import os
import time
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from app.config import get_config
from app.context import get_context
from app.postgres import init_database
from app.redis import init_cache
from app.hook import init_hooks
from app.log import get_log
from app.helpers.secret_helper import secret_exists, secret_read
from app.helpers.lock_helper import lock_exists, lock_disable
from app.helpers.uptime_helper import Uptime
from app.error import (
    ERR_SERVER_LOCKED, ERR_SERVER_FORBIDDEN, ERR_SERVER_ERROR,
    ERR_FILE_NOT_FOUND)
from app.version import __version__
from app.routers import (
    token_retrieve_router,
    token_invalidate_router,
    user_register_router,
    user_login_router,
    user_select_router,
    user_update_router,
    user_password_router,
    user_role_router,
    user_delete_router,
    user_list_router,
    userpic_upload_router,
    userpic_retrieve_router,
    userpic_delete_router,
    collection_insert_router,
    collection_select_router,
    collection_update_router,
    collection_delete_router,
    collection_list_router,
    document_upload_router,
    document_select_router,
    document_update_router,
    document_move_router,
    document_delete_router,
    document_list_router,
    document_download_router,
    thumbnail_retrieve_router,
    tag_insert_router,
    tag_delete_router,
    tag_list_router,
    setting_insert_router,
    setting_list_router,
    secret_retrieve_router,
    secret_delete_router,
    lock_create_router,
    lock_retrieve_router,
    telemetry_retrieve_router,
    execute_router,
)

cfg = get_config()
ctx = get_context()
log = get_log()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup tasks such as disabling the app lock, initializing
    the database, and running app hooks before yielding control to the
    app.
    """
    await lock_disable()
    await init_database()
    await init_cache()
    await init_hooks()
    yield


uptime = Uptime()

app = FastAPI(lifespan=lifespan, title="Hidden", version=__version__)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

app.include_router(user_login_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(token_retrieve_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(token_invalidate_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(user_register_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(user_select_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(user_update_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(user_password_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(user_role_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(user_delete_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(user_list_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(userpic_upload_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(userpic_delete_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(collection_insert_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(collection_select_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(collection_update_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(collection_delete_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(collection_list_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(document_upload_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(document_select_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(document_update_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(document_move_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(document_delete_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(document_list_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(tag_insert_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(tag_delete_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(tag_list_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(setting_insert_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(setting_list_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(secret_retrieve_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(secret_delete_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(lock_create_router.router, prefix=cfg.APP_API_VERSION)
app.include_router(lock_retrieve_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(telemetry_retrieve_router.router, prefix=cfg.APP_API_VERSION)  # noqa E501
app.include_router(execute_router.router, prefix=cfg.APP_API_VERSION)

app.include_router(userpic_retrieve_router.router)
app.include_router(document_download_router.router)
app.include_router(thumbnail_retrieve_router.router)

app.mount(cfg.SPHINX_URL, StaticFiles(directory=cfg.SPHINX_PATH, html=True),
          name=cfg.SPHINX_NAME)


@app.get("/{full_path:path}", include_in_schema=False,)
async def catch_all(full_path: str, request: Request):
    """
    Serves static files for unmatched routes. Returns the main HTML file
    if no specific path is provided, or serves the requested file if it
    exists.
    """
    if not full_path or full_path == cfg.HTML_FILE:
        file_path = os.path.join(cfg.HTML_PATH, cfg.HTML_FILE)
        with open(file_path) as f:
            return HTMLResponse(content=f.read())

    else:
        file_path = os.path.join(cfg.HTML_PATH, full_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=ERR_FILE_NOT_FOUND)
        else:
            return FileResponse(file_path)


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    """
    Intercepts each HTTP request to check for lock and secret key
    presence, attaches request-related context information, and logs
    request and response details.
    """
    if await lock_exists():
        raise HTTPException(status_code=423, detail=ERR_SERVER_LOCKED)

    elif not await secret_exists():
        raise HTTPException(status_code=403, detail=ERR_SERVER_FORBIDDEN)

    ctx.request_start_time = time.time()
    ctx.request_uuid = str(uuid4())
    ctx.secret_key = await secret_read()
    ctx.request = request

    log.debug(
        "request received; module=app; function=middleware_handler; "
        f"elapsed_time=0; method={request.method}; url={request.url.path};")

    response = await call_next(request)

    elapsed_time = "{0:.6f}".format(time.time() - ctx.request_start_time)
    log.debug(
        "response sent; module=app; function=middleware_handler; "
        f"elapsed_time={elapsed_time}; status={response.status_code};")

    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception):
    """
    Handles exceptions with special processing for 403, 423 and 404
    errors raised in a separate middleware. Also handles validation
    error by returning a 422 status with detailed error information.
    For other exceptions, it logs the error and returns a 500 internal
    server error response. All responses are JSON-formatted with error
    details and include CORS headers for cross-origin requests.
    """
    if isinstance(e, ValidationError):
        response = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": e.errors()}))

    elif isinstance(e, HTTPException) and e.status_code == 403:
        response = JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=jsonable_encoder({"detail": e.detail}))

    elif isinstance(e, HTTPException) and e.status_code == 423:
        response = JSONResponse(
            status_code=status.HTTP_423_LOCKED,
            content=jsonable_encoder({"detail": e.detail}))

    elif isinstance(e, HTTPException) and e.status_code == 404:
        response = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": e.detail}))

    else:
        elapsed_time = "{0:.6f}".format(time.time() - ctx.request_start_time)
        log.error(f"error raised; elapsed_time={elapsed_time}; e={str(e)};")

        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"detail": ERR_SERVER_ERROR}))

    return add_cors_headers(response)


def add_cors_headers(response: JSONResponse) -> JSONResponse:
    """
    Adds the necessary headers to the response to allow cross-origin
    requests from any source. This ensures that the response can be
    accessed by clients from different domains, supports all HTTP
    methods and headers, and allows credentials to be included in
    requests. The function modifies and returns the response with
    these headers to enable proper cross-origin resource sharing.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response
