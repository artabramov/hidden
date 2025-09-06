import time
from fastapi import FastAPI, Request, status, HTTPException
from app.config import get_config
from app.openapi import OPENAPI_TAGS, OPENAPI_DESCRIPTION, OPENAPI_PREFIX
from app.sqlite import SessionManager, init_database
from app.redis import RedisClient, init_cache
from app.managers.file_manager import FileManager
from app.lru import LRU
from app.hook import init_hooks
from app.log import init_logger, bind_request_logger
from contextlib import asynccontextmanager
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
    collection_insert
)
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
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.version import __version__
from app.error import (
    HTTP_498_SECRET_KEY_MISSING, HTTP_499_SECRET_KEY_INVALID,
    ERR_SECRET_KEY_MISSING, ERR_SECRET_KEY_INVALID, ERR_LOCKED,
    ERR_SERVER_ERROR
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes core services and a shared file manager on startup. On
    shutdown, disposes database resources and closes cache connections.
    """
    config = get_config()
    app.state.config = config

    app.state.sessionmanager = SessionManager(
        sqlite_path=config.SQLITE_PATH,
        sql_echo=config.SQLITE_SQL_ECHO,
    )
    await init_database(app.state.sessionmanager)

    app.state.redis_client = RedisClient(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        decode_responses=config.REDIS_DECODE_RESPONSES,
    )
    await init_cache(app.state.redis_client)

    init_hooks(app)
    init_logger(app)

    file_manager = FileManager(config)
    app.state.file_manager = file_manager

    app.state.lru = LRU(
        config.LRU_TOTAL_SIZE_BYTES,
        item_size_bytes=config.LRU_ITEM_SIZE_LIMIT_BYTES
    )

    lock_path = config.LOCK_FILE_PATH
    if await file_manager.isfile(lock_path):
        await file_manager.delete(lock_path)

    try:
        yield
    finally:
        await app.state.sessionmanager.async_engine.dispose()
        await app.state.redis_client.close()


app = FastAPI(
    title="Hidden",
    version=__version__,
    openapi_tags=OPENAPI_TAGS,
    description=OPENAPI_DESCRIPTION,
    openapi_prefix=OPENAPI_PREFIX,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    },
)

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


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    """
    Binds a request-scoped logger, logs request timing, checks lockdown
    state, reads the secret key, appends X-Request-ID to the response.
    """
    file_manager = request.app.state.file_manager

    request.state.log = bind_request_logger(request)
    request.state.log.debug(
        f"request received; elapsed_time=0; "
        f"method={request.method}; url={request.url.path};"
    )

    lock_path = request.app.state.config.LOCK_FILE_PATH
    if await file_manager.isfile(lock_path):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=[{"type": ERR_LOCKED,
                     "msg": "Application is locked"}])

    secret_path = request.app.state.config.SECRET_KEY_PATH
    if not await file_manager.isfile(secret_path):
        request.app.state.lru.clear()
        raise HTTPException(
            status_code=HTTP_498_SECRET_KEY_MISSING,
            detail=[{"type": ERR_SECRET_KEY_MISSING,
                     "msg": "Secret key is missing"}])

    secret_key = (await file_manager.read(secret_path)).strip()
    secret_length = request.app.state.config.SECRET_KEY_LENGTH
    if not secret_key or len(secret_key) != secret_length:
        request.app.state.lru.clear()
        raise HTTPException(
            status_code=HTTP_499_SECRET_KEY_INVALID,
            detail=[{"type": ERR_SECRET_KEY_INVALID,
                     "msg": "Secret key is invalid"}])

    request.state.secret_key = secret_key
    response = await call_next(request)

    elapsed_time = f"{time.time() - request.state.request_start_time:.6f}"
    request.state.log.debug(
        f"response sent; elapsed_time={elapsed_time}; "
        f"status_code={response.status_code};"
    )

    response.headers["X-Request-ID"] = request.state.request_uuid
    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception):
    """
    Handles exceptions and returns consistent JSON errors; logs elapsed
    time (with stack trace for server errors) and appends X-Request-ID.
    """
    if isinstance(e, (RequestValidationError, ValidationError)):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = getattr(e, "errors", lambda: [])()

    elif isinstance(e, (
        InvalidTag, InvalidSignature, InvalidKey, UnsupportedAlgorithm,
        AlreadyFinalized, NotYetFinalized, AlreadyUpdated, InternalError)
    ):
        request.app.state.lru.clear()
        status_code = HTTP_499_SECRET_KEY_INVALID
        detail=[{"type": ERR_SECRET_KEY_INVALID,
                 "msg": "Secret key is invalid"}]

    elif isinstance(e, HTTPException):
        status_code = e.status_code
        detail = e.detail

    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail=[{"type": ERR_SERVER_ERROR,
                 "msg": "Internal server error"}]

    elapsed_time = f"{time.time() - request.state.request_start_time:.6f}"
    request.state.log.error(
        "request failed; elapsed_time=%s; status_code=%s; e=%s;",
        elapsed_time, status_code, str(e), exc_info=True,
    )

    response = JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"detail": detail}),
    )
    response.headers["X-Request-ID"] = request.state.request_uuid
    return response
