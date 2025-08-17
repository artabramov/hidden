"""
Main FastAPI application entrypoint that initializes the app,
configures middleware for request validation, logging and context
management, performs startup tasks, mounts static assets and
documentation, registers all API routers and installs a global
exception handler.
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
from app.error import ERR_SERVER_LOCKED, ERR_SERVER_FORBIDDEN, ERR_SERVER_ERROR
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
    Handles application startup by disabling the lock if present,
    initializing the database and cache, running registered hooks
    and then yielding control back to FastAPI.
    """
    await lock_disable()
    await init_database()
    await init_cache()
    await init_hooks(app)
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
    Serves static content for unmatched routes by returning the
    requested file if it exists under HTML_PATH or falling back to the
    main HTML file as the entry point for the single-page application.
    """
    file_path = os.path.join(cfg.HTML_PATH, full_path)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    with open(os.path.join(cfg.HTML_PATH, cfg.HTML_FILE)) as f:
        return HTMLResponse(content=f.read())


app.mount("/", StaticFiles(directory=cfg.HTML_PATH, html=True), name="/")


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    """
    Processes each request by checking for a server lock or missing
    secret key, attaching context such as start time, UUID, request
    object and secret key, and logging basic request and response
    information with elapsed time.
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
    Handles exceptions by returning JSON responses for validation
    errors, selected HTTP errors and unexpected failures, logging
    server-side errors when necessary and appending permissive CORS
    headers to all responses.
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
    Adds permissive CORS headers to the response, effectively
    duplicating the behavior of CORSMiddleware and allowing any
    origin with credentials.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response
