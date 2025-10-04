"""
Hidden — main application module.

This module assembles the FastAPI application, connects core services,
mounts all routers, and defines global behavior. On startup, it loads
configuration, opens database and cache connections, and places shared
components into the application state. If lockdown mode is enabled, it
is forcibly disabled. On shutdown, all resources are released cleanly.

For every request, assign a UUID, measure and log duration, check the
lockdown state, and validate the gocryptfs key. Request logging is
enabled at DEBUG level.

Errors are handled centrally to produce consistent JSON. Returns 422 for
validation; 498/499 for gocryptfs-key issues; 423 for lockdown mode; 409
for file conflicts; 401/403 for auth errors. All other exceptions become
500. Every non-validation issue is logged with elapsed time and a stack
trace, and the response includes the request UUID (X-Request-ID). Error
logging is enabled at ERROR level.
"""

import time
import asyncio
import logging
from uuid import uuid4
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from cryptography.exceptions import (
    InvalidTag,
    InvalidSignature,
    InvalidKey,
    UnsupportedAlgorithm,
    AlreadyFinalized,
    NotYetFinalized,
    AlreadyUpdated,
    InternalError,
)
from app.config import get_config
from app.sqlite import SessionManager, init_database
from app.redis import RedisClient, init_cache
from app.managers.file_manager import FileManager
from app.lru import LRU
from app.hook import init_hooks
from app.rwlock import RWLock
from app.log import init_logger
from app.routers import (
    token_retrieve,
    token_invalidate,
    user_register,
    user_login,
    user_role,
    user_password,
    user_select,
    user_update,
    user_delete,
    user_list,
    userpic_upload,
    userpic_delete,
    userpic_retrieve,
    collection_insert,
    collection_select,
    collection_update,
    collection_delete,
    collection_list,
    document_upload,
    document_download,
    document_select,
    document_update,
    document_delete,
    document_list,
    thumbnail_retrieve,
)
from app.version import __version__
from app.error import (
    HTTP_498_GOCRYPTFS_KEY_MISSING, HTTP_499_GOCRYPTFS_KEY_INVALID,
    ERR_GOCRYPTFS_KEY_MISSING, ERR_GOCRYPTFS_KEY_INVALID, ERR_LOCKED,
    ERR_SERVER_ERROR)

# NOTE: Use a project-wide search for comments with the "NOTE" prefix
# to read all design and behavior caveats. Each comment starts with a
# scope cue for quick scanning.

OPENAPI_PREFIX = "/api/v1"
OPENAPI_TITLE = "Hidden — REST over gocryptfs"
OPENAPI_DESCRIPTION = """
Secure file storage with gocryptfs-key protection,
file versioning, and irreversible deletion —
[joinhidden.com](https://joinhidden.com)
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes core services and a shared file manager on startup. On
    shutdown, disposes database resources and closes cache connections.
    """

    # NOTE: On app startup, core services are placed in app state for
    # global access: config, database connection, cache client, logger,
    # file manager, LRU cache, locks.

    config = get_config()
    app.state.config = config

    app.state.sessionmanager = SessionManager(
        sqlite_path=config.SQLITE_PATH,
        sql_echo=config.SQLITE_SQL_ECHO)
    await init_database(app.state.sessionmanager)

    app.state.redis_client = RedisClient(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        decode_responses=config.REDIS_DECODE_RESPONSES)
    await init_cache(app.state.redis_client)

    init_hooks(app)
    init_logger(app)

    file_manager = FileManager(config)
    app.state.file_manager = file_manager

    # NOTE: Thumbnails/userpics are cached in an in-memory LRU.
    # App lockdown or gocryptfs-key errors clear the LRU immediately.

    app.state.lru = LRU(
        config.LRU_TOTAL_SIZE_BYTES,
        item_size_bytes=config.LRU_ITEM_SIZE_LIMIT_BYTES)

    # NOTE: On app startup, a global app lock file is removed
    # if present (the lockdown mode is forcibly disabled).

    lock_path = config.LOCK_FILE_PATH
    if await file_manager.isfile(lock_path):
        await file_manager.delete(lock_path)

    # NOTE: On app startup, per-process locks are placed in app state.
    # Not shared across workers (use one worker or create a distributed
    # lock, e.g. Redis). Lock order: collection first, then files. When
    # locking multiple files, sort keys to avoid AB-BA deadlocks.

    app.state.collection_locks = defaultdict(RWLock)
    app.state.file_locks = defaultdict(asyncio.Lock)

    try:
        yield
    finally:
        await app.state.sessionmanager.async_engine.dispose()
        await app.state.redis_client.close()


app = FastAPI(
    title=OPENAPI_TITLE,
    version=__version__,
    description=OPENAPI_DESCRIPTION,
    root_path=OPENAPI_PREFIX,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    }
)

# TODO: Hide the user deletion router from public API.

app.include_router(user_login.router)
app.include_router(token_retrieve.router)
app.include_router(token_invalidate.router)
app.include_router(user_register.router)
app.include_router(user_role.router)
app.include_router(user_password.router)
app.include_router(user_select.router)
app.include_router(user_update.router)
app.include_router(user_delete.router)
app.include_router(user_list.router)
app.include_router(userpic_upload.router)
app.include_router(userpic_delete.router)
app.include_router(userpic_retrieve.router)
app.include_router(collection_insert.router)
app.include_router(collection_select.router)
app.include_router(collection_update.router)
app.include_router(collection_delete.router)
app.include_router(collection_list.router)
app.include_router(document_upload.router)
app.include_router(document_download.router)
app.include_router(document_select.router)
app.include_router(document_update.router)
app.include_router(document_delete.router)
app.include_router(document_list.router)
app.include_router(thumbnail_retrieve.router)


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    """
    Binds a request-scoped logger, logs request timing, checks lockdown
    state, reads the gocryptfs key, appends X-Request-ID to the response.
    """
    file_manager = request.app.state.file_manager

    # NOTE: For each request, generate UUID (or reuse X-Request-ID),
    # time it, log the response. Logs are emitted only at DEBUG level.

    request.state.request_uuid = str(uuid4())
    request.state.request_start_time = time.time()

    base = request.app.state.log
    request.state.log = logging.LoggerAdapter(base, {
        "request_uuid": request.state.request_uuid})

    request.state.log.debug(
        f"request received; method={request.method}; "
        f"url={request.url.path};")

    # NOTE: Before handling each request, check the global application
    # lock file; if present, raise error and short-circuit the request.

    lock_path = request.app.state.config.LOCK_FILE_PATH
    if await file_manager.isfile(lock_path):
        request.app.state.lru.clear()
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=[{"type": ERR_LOCKED,
                     "msg": "Application is locked"}])

    # NOTE: Before handling each request, validate the gocryptfs key;
    # store it in request state and keep it request-scoped (not shared
    # outside the current request).

    gocryptfs_path = request.app.state.config.GOCRYPTFS_PASSPHRASE_PATH
    if not await file_manager.isfile(gocryptfs_path):
        request.app.state.lru.clear()
        raise HTTPException(
            status_code=HTTP_498_GOCRYPTFS_KEY_MISSING,
            detail=[{"type": ERR_GOCRYPTFS_KEY_MISSING,
                     "msg": "gocryptfs key is missing"}])

    gocryptfs_key = (await file_manager.read(gocryptfs_path)).strip()
    gocryptfs_key_length = request.app.state.config.GOCRYPTFS_PASSPHRASE_LENGTH
    if not gocryptfs_key or len(gocryptfs_key) != gocryptfs_key_length:
        request.app.state.lru.clear()
        raise HTTPException(
            status_code=HTTP_499_GOCRYPTFS_KEY_INVALID,
            detail=[{"type": ERR_GOCRYPTFS_KEY_INVALID,
                     "msg": "gocryptfs key is invalid"}])

    request.state.gocryptfs_key = gocryptfs_key
    response = await call_next(request)

    elapsed_time = f"{time.time() - request.state.request_start_time:.6f}"
    request.state.log.debug(
        f"response sent; elapsed_time={elapsed_time}; "
        f"status_code={response.status_code};")

    response.headers["X-Request-ID"] = request.state.request_uuid
    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception):
    """
    Handles exceptions and returns consistent JSON errors; logs elapsed
    time (with stack trace for server errors) and appends X-Request-ID.
    """

    # NOTE: During request handling, all uncaught exceptions are routed
    # to the exception handler to return consistent JSON and log elapsed
    # time: validation at DEBUG; others at ERROR (with stack trace).

    if isinstance(e, (RequestValidationError, ValidationError)):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = getattr(e, "errors", lambda: [])()

    elif isinstance(e, (
        InvalidTag, InvalidSignature, InvalidKey, UnsupportedAlgorithm,
        AlreadyFinalized, NotYetFinalized, AlreadyUpdated, InternalError)
    ):
        request.app.state.lru.clear()
        status_code = HTTP_499_GOCRYPTFS_KEY_INVALID
        detail = [{"type": ERR_GOCRYPTFS_KEY_INVALID,
                   "msg": "gocryptfs key is invalid"}]

    elif isinstance(e, HTTPException):
        status_code = e.status_code
        detail = e.detail

    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = [{"type": ERR_SERVER_ERROR,
                   "msg": "Internal server error"}]

    # Validation errors are logged at DEBUG; all others at ERROR
    elapsed_time = f"{time.time() - request.state.request_start_time:.6f}"
    if status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        request.state.log.debug(
            f"response sent; elapsed_time={elapsed_time}; "
            f"status_code={status_code};")

    else:
        request.state.log.error(
            "request failed; elapsed_time=%s; status_code=%s; e=%s;",
            elapsed_time, status_code, str(e), exc_info=True)

    response = JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"detail": detail}))
    response.headers["X-Request-ID"] = request.state.request_uuid
    return response
